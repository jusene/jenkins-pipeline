#!/usr/bin/env python
# -*- coding=utf-8 -*-

class Config:
    DOCKER_REGISTRY = 'reg.ops.com'
    DOCKER_REGISTRY_PRO = 'reg.k8s.com'
    HOST_IP = "192.168.66.92"
    HUAYUN_BIN = ['huayun-lab-auth', 'huayun-lab-report', 'huayun-lab-data']
    AI_BIN = ['ai-lab-auth', 'ai-lab-report', 'ai-lab-data']
    ARCH_BIN = ['service-linux-user', 'service-lab-env']
    FONTS = ["ai-lab-resource", "huayun-lab-resource", "iot-service-device", "iot-service-course", "service-iot-device", "service-course"]
    STATS = ["ai-lab-stat", "huayun-lab-stat"]
    CERTS = ["iot-service-lab", "service-iot-lab"]


class DevConfig(Config):
    def __init__(self):
        self.stat_target = "192.168.66.121"
        self.service_config = 18804
        self.service_exam = 18803
        self.service_exam_report = 18806
        self.service_order = 18807
        self.service_resource = 18801
        self.service_sms = 18805
        self.service_user = 18802
        self.service_chat = 18812
        self.service_comment = 18813
        self.service_course = 18809
        self.service_iot_device = 18811
        self.service_iot_lab = 18810
        self.service_msg_recommend = 18814
        self.service_linux_user = 18821 
        self.service_vmmanage = 18820
        self.service_lab_competition = 18822
        self.service_lab_data = 18825
        self.service_lab_env = 18824
        self.service_lab_report = 18826

class TestConfig(Config):
    def __init__(self):
        self.service_config = 28804
        self.service_exam = 28803
        self.service_exam_report = 28806
        self.service_order = 28807
        self.service_resource = 28801
        self.service_sms = 28805
        self.service_user = 28802
        self.service_chat = 28812
        self.service_comment = 28813
        self.service_course = 28809
        self.service_iot_device = 28811
        self.service_iot_lab = 28810
        self.service_msg_recommend = 28814
        self.service_linux_user = 28821 
        self.service_vmmanage = 28820
        self.service_lab_competition = 28822
        self.service_lab_data = 28825
        self.service_lab_env = 28824
        self.service_lab_report = 28826


class ProdConfig(Config):
    def __init__(self):
        pass        

config = {
    'dev': DevConfig(),
    'local': DevConfig(),
    'test': TestConfig(),
    'prod': ProdConfig(),
    'cloud': ProdConfig(),
    'arm': ProdConfig()
}
