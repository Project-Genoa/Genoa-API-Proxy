import json
import os

class ProxyAddon:
    def __init__(self):
        self.template = """---
title: [REQUEST_PATH]
parent: Raw Packet Documentation
layout: default
---

# [REQUEST_PATH]

## Description
An endpoint

### [REQUEST_TYPE] Arguments

[REQUEST_TABLE]


## Response
~~~json
[RESPONSE_JSON]
~~~

### result

[RESPONSE_TABLE]
"""

    def createTable(self, dictData):
        table = []
        largestParameter = 0
        largestValue = 0
        for parameter in dictData.keys():
            if (len(parameter)) > largestParameter:
                largestParameter = len(parameter)
        for parameter in dictData.keys():
            if (len(str(dictData[parameter]))) > largestValue:
                largestValue = len(str(dictData[parameter]))

        if (len("Parameter") > largestParameter):
            largestParameter = len("Parameter")
        if (len("Example Value") > largestValue):
            largestValue = len("Example Value")

        table.append('| Parameter' + ' '*(largestParameter-len('Parameter')) + ' | Example Value' + ' '*(largestValue-len('Example Value')) + ' | Description |')
        table.append('|-' + '-'*largestParameter + '-|-' + '-'*largestValue + '-|-------------|')

        for parameter in dictData.keys():
            table.append('| ' + str(parameter) + ' '*(largestParameter-len(parameter)) + ' | ' + str(dictData[parameter]) + ' '*(largestValue-len(str(dictData[parameter]))) + ' | Description |')

        return '\n'.join(table)

    def response(self, flow):
        if ('availableresourcepack' in flow.request.path):
            print('streaming...')
            flow.response.stream = True
        else:
            docFile = self.template.replace("[REQUEST_PATH]", flow.request.path.split('?')[0])
            docFile = docFile.replace("[REQUEST_TYPE]", flow.request.method)

            if (flow.response.status_code == 200):
                try:
                    docFile = docFile.replace("[RESPONSE_JSON]", json.dumps(json.loads(str(flow.response.content, encoding='utf-8')), indent=4))
                except:
                    docFile = docFile.replace("[RESPONSE_JSON]", str(flow.response.content, encoding='utf-8'))

                if (flow.request.method == 'GET'):
                    #print(flow.request.query)
                    if (len(list(flow.request.query.keys())) > 0):
                        docFile = docFile.replace("[REQUEST_TABLE]", self.createTable(flow.request.query))
                    else:
                        docFile = docFile.replace("[REQUEST_TABLE]", "[NO ARGUMENTS]")
                else:
                    if (str(flow.request.content, encoding='utf-8') != '' and str(flow.request.content, encoding='utf-8') != None):
                        docFile = docFile.replace("[REQUEST_TABLE]", self.createTable(json.loads(str(flow.request.content, encoding='utf-8'))))
                    else:
                        docFile = docFile.replace("[REQUEST_TABLE]", "[NO ARGUMENTS]")

                try:
                    if (len(list(json.loads(str(flow.response.content, encoding='utf-8')))) < 100 ):
                        docFile = docFile.replace("[RESPONSE_TABLE]", self.createTable(json.loads(str(flow.response.content, encoding='utf-8'))["result"]))
                    else:
                        docFile = docFile.replace("[RESPONSE_TABLE]", "[TOO MANY PARAMETERS]")
                except:
                    try:
                        docFile = docFile.replace("[RESPONSE_TABLE]", self.createTable(json.loads(str(flow.response.content, encoding='utf-8'))))
                    except:
                        pass


                savePath = os.path.join(flow.request.path.split('?')[0])
                savePath = './documentation' + savePath + '.md'

                os.makedirs('/'.join(savePath.split('/')[:-1]), exist_ok=True)#
                with open(savePath, 'w') as file:
                    file.write(docFile)


addons = [ProxyAddon()]