#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Hussein Omar, CSS - ANZ"
__email__ = "husseino@cisco.com"
__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2021 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

# ---> Imports
from datetime import datetime
from threading import Thread
import csv
import ipaddress
import getpass
import requests
import json
import time
from alive_progress import alive_bar
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ---> Main Code


class vpoc():
    def __init__(self):
        pass

    def login(self):
        '''
        - Receive user input for vmanage information ip-address/username/password
        - Contruct API call base-URL
        '''
        print('''
    |=================================================|
    | Title < Tool Name >      |
    | ------------------------------------------      |
    | some description about what the tool does and   |
    | and who is supposed to used with disclaimers    |
    |                                                 |
    | This is Cisco Internal too and not for external |
    | distribution                                    |
    | For any questions contact husseino@cisco.com    |
    |=================================================|
''')
        self.vmanage_ip = None
        while self.vmanage_ip == None:
            vmanage_ip_typed = input('vManage IP address: ')
            try:
                self.vmanage_ip = ipaddress.ip_address(vmanage_ip_typed)
            except Exception:
                print(
                    f'ERROR: {vmanage_ip_typed} is not a correct IPv4 or IPv6 address')

        self.port = input('Port Number (default 8443): ')
        if len(self.port) == 0:
            self.port = 8443
        self.username = input('Username: ')
        self.password = getpass.getpass('Password: ')
        self.base_url = f'https://{self.vmanage_ip}:{self.port}'

    def getCookie(self):
        '''
        - Initial first login to vManage and return authentication cookie
        '''
        mount_url = '/j_security_check'
        url = self.base_url + mount_url
        # Format data for loginForm
        payload = {'j_username': self.username, 'j_password': self.password}
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache"
        }
        self.response = requests.request(
            "POST", url, data=payload, headers=headers, verify=False)

        if self.response.status_code >= 300:
            raise BaseException(
                "ERROR : The username/password is not correct.")
        if '<html>' in self.response.text:
            raise BaseException("ERROR : Login Failed.")
        print('--------------------------------------------------------')
        print(f'Authenticated, login to {self.vmanage_ip} is SUCCESSFUL')
        print('--------------------------------------------------------')
        self.cookie = str(self.response.cookies).split(' ')[1]

    def getToken(self):
        '''
        - Generate authentication token to be used in subsequent requests
        '''
        mount_url = '/dataservice/client/token'
        url = self.base_url + mount_url
        # Format data for loginForm
        payload = {}
        headers = {
            'Cookie': self.cookie,
        }
        self.response2 = requests.request(
            "GET", url, data=payload, headers=headers, verify=False)
        self.token = self.response2.text

    def auth(self):
        '''
        - First method to be called in main App
        - Returns session cookie and token
        '''
        vpoc.login(self)
        vpoc.getCookie(self)
        vpoc.getToken(self)

#################################################################
#################### API calls Functions #######################

    def getDataResponse(self, mountURL):
        '''
        - Args: mounting URL
        - Construct full URL by adding mountURL to baseURL
        - Send a 'GET' request with empty payload with cookie and token
        - Return the data portion (dict) of the JSON response
        '''
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            'X-XSRF-TOKEN': self.token,
            'Cookie': self.cookie
        }
        url = self.base_url + mountURL
        response = requests.request("GET", url, headers=headers, verify=False)
        data = json.loads(response.text)['data']
        return data

    def getFullResponse(self, mountURL):
        '''
        - Args: mounting URL
        - Construct full URL by adding mountURL to baseURL
        - Send a 'GET' request with empty payload with cookie and token
        - Return the data portion (dict) of the JSON response
        '''
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            'X-XSRF-TOKEN': self.token,
            'Cookie': self.cookie
        }
        url = self.base_url + mountURL
        response = requests.request("GET", url, headers=headers, verify=False)
        return response.text

    def postRequest(self, mountURL, payload):
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            'X-XSRF-TOKEN': self.token,
            'Cookie': self.cookie
        }
        url = self.base_url + mountURL
        response = requests.request(
            "POST", url, headers=headers, data=payload, verify=False)
        return response

#################################################################
################## Tools Functions ##############################

    def dict2csv(self, dict, filename, fieldnames):
        with open(filename, 'w') as csvFile:
            wr = csv.DictWriter(csvFile, fieldnames=fieldnames)
            wr.writeheader()
            for ele in dict:
                wr.writerow(ele)
        print(
            '------------------------------------------------------------------------------')
        print(f'->>> File {filename} has been written to disk')
        print(
            '------------------------------------------------------------------------------')

    def exportTxt(self, text, filename):
        file = open(filename, 'a')
        file.write(text)
        file.close()
        print(
            '------------------------------------------------------------------------------')
        print(f'->>> File {filename} has been written to disk')
        print(
            '------------------------------------------------------------------------------')

########################## core functions ###############################

    def getDevices(self):
        '''
        Generate list of devices that are activated and configured.
        '''
        mountURL = '/dataservice/system/device/vedges'
        data = vpoc.getDataResponse(self, mountURL)
        devices = []
        for item in data:
            try:
                if item['system-ip']:
                    devices.append(item)
            except:
                pass
        exportData = []
        for item in devices:
            deviceData = {}
            deviceData['host-name'] = item['host-name']
            deviceData['system-ip'] = item['system-ip']
            deviceData['configOperationMode'] = item['configOperationMode']
            try:
                deviceData['template'] = item['template']
            except:
                deviceData['template'] = 'no-template-attached'
            deviceData['vmanageConnectionState'] = item['vmanageConnectionState']
            deviceData['chasisNumber'] = item['chasisNumber']
            exportData.append(deviceData)
        return exportData

    def vmanageModeDevices(self, filename):
        '''
        This function will create three CSV files with device list
        and template operation mode.
        '''
        devices = vpoc.getDevices(self)
        vmanagedDevices = []
        for item in devices:
            if item['configOperationMode'] == 'vmanage':
                vmanagedDevices.append(item)
        fieldNames = ['host-name', 'system-ip',
                      'configOperationMode', 'template', 'vmanageConnectionState', 'chasisNumber']
        vpoc.dict2csv(self, vmanagedDevices,
                      filename, fieldNames)
        return vmanagedDevices

    def cliModeDevices(self, filename):
        '''
        This function will create three CSV files with device list
        and template operation mode.
        '''
        devices = vpoc.getDevices(self)
        cliDevices = []
        for item in devices:
            if item['configOperationMode'] == 'cli':
                cliDevices.append(item)
        fieldNames = ['host-name', 'system-ip',
                      'configOperationMode', 'template', 'vmanageConnectionState', 'chasisNumber']
        vpoc.dict2csv(self, cliDevices, filename, fieldNames)
        return cliDevices

    def getCliConfig(self, device, filename):
        '''
        This function will create text file with device system-ip
        containting cli running configuration
        '''
        mountURL = f'/dataservice/template/config/running/{device["chasisNumber"]}'
        data = json.loads(vpoc.getFullResponse(self, mountURL))['config']
        vpoc.exportTxt(self, data, filename)

    def mode2Cli(self, device):
        requestBody = {"deviceType": "vedge", "devices": [
            {"deviceId": "", "deviceIP": ""}]}
        requestBody['devices'][0]['deviceId'] = str(device['chasisNumber'])
        requestBody['devices'][0]['deviceIP'] = str(device['system-ip'])
        requestBody = json.dumps(requestBody)
        mountURL = '/dataservice/template/config/device/mode/cli'
        response = vpoc.postRequest(self, mountURL, requestBody)
        print(
            '------------------------------------------------------------------------------')
        print(
            f'->>> Changing {device["host-name"]}-{device["system-ip"]} to CLI mode')
        print(
            '------------------------------------------------------------------------------')

    def task3(self, system_ip, filename):
        devices = vpoc.getDevices(self)
        for device in devices:
            if device['system-ip'] == system_ip:
                config = vpoc.getCliConfig(self, device, filename)

    def task5(self, system_ip):
        devices = vpoc.getDevices(self)
        for device in devices:
            if device['system-ip'] == system_ip:
                config = vpoc.mode2Cli(self, device)


def main():
    session = vpoc()
    session.auth()
    devices = session.getDevices()

    def getTimeStamp():
        dateTimeObj = datetime.now()
        timestampStr = dateTimeObj.strftime("%d%m%Y-%H%M%S")
        return timestampStr

    def task1():
        filename = input(
            'Please enter file name with .csv extension (default = vManage-Mode-Devices-<timeStamp>.csv): ')
        if filename == '':
            filename = f'vManage-Mode-Devices-{getTimeStamp()}.csv'
        session.vmanageModeDevices(filename)

    def task2():
        filename = input(
            'Please enter file name with .csv extension (default = CLI-Mode-Devices-<timeStamp>.csv): ')
        if filename == '':
            filename = f'CLI-Mode-Devices-{getTimeStamp()}.csv'
        session.cliModeDevices(filename)

    def task3():
        system_ip = input(
            'Please enter device-system-ip: ')
        filename = input(
            'Please enter file name with .txt extension (default = System-IP-<timeStamp>.txt): ')
        if filename == '':
            filename = f'{system_ip}-{getTimeStamp()}.txt'
        session.task3(system_ip, filename)

    def task4():
        print('--------------------------------------------------')
        print('       Generating running-config for all device   ')
        print('--------------------------------------------------')
        print('')
        with alive_bar(len(devices)) as bar:
            for device in devices:
                filename = f'{device["system-ip"]}-{getTimeStamp()}.txt'
                session.getCliConfig(device, filename)
                bar()
                time.sleep(5)
        print('')

    def task5():
        system_ip = input(
            'Please enter device-system-ip: ')
        session.task5(system_ip)

    def task6():
        print('--------------------------------------------------')
        print('       Converting all devices to CLI mode         ')
        print('--------------------------------------------------')
        print('')
        with alive_bar(len(devices)) as bar:
            for device in devices:
                if device['configOperationMode'] == 'vmanage':
                    session.mode2Cli(device)
                bar()
                time.sleep(5)
        print('')

    def promptOptions():
        print('''
        Please choose one of the following options:
            [1] Generate list of device in vManage Mode
            [2] Generate list of device in CLI Mode
            [3] Generate running config in .txt for spefic device
            [4] Generate running config in .txt for all deivces
            [5] Convert specific devide to CLI mode
            [6] Convert all devices from vManage Mode to CLI mode
            [7] Exit''')

        task_id = input('Please input number from 1 - 7: ')
        return task_id

    task_id = '0'
    while task_id != '00':
        task_id = promptOptions()
        if task_id == '1':
            task1()
        if task_id == '2':
            task2()
        if task_id == '3':
            task3()
        if task_id == '4':
            task4()
        if task_id == '5':
            task5()
        if task_id == '6':
            task6()
        if task_id == '7':
            exit()

    if session.cookie:
        promptOptions()


if __name__ == '__main__':
    main()
