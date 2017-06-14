#coding=utf-8

#外界给封装的查询方法里提供需要查询的用户列表
def getAccount():
    account_list=[{'name':'刘称院','phone':'18676780252'},{'name':'陈崇文','phone':'15112643691'},{'name':'吴瑶','phone':'18390780691'},
                  {'name':'罗美婵','phone':'13903011645'},{'name':'武学平','phone':'18976585566'},{'name':'刘燕妮','phone':'18776111166'},
                  {'name':'戴盛生','phone':'13801918367'},{'name':'农春影','phone':'13878833360'},{'name':'熊菲','phone':'15310618883'},
                  {'name':'刘家灯','phone':'13825037381'},{'name':'陈燕玲','phone':'13798426692'},{'name':'廖敬城','phone':'13760454549'},
                  # {'name':'张国玉','phone':'15626952003'},{'name':'郭俊锴','phone':'18580865372'},{'name':'陈观礼', 'phone':'13763016263'},
                  # {'name':'冉鎧','phone':'15923820357'},{'name':'史磊','phone':'13122708983'},{'name':'何光华','phone':'18376065847'},
                  # {'name':'赵粉如', 'phone':'13316593483'},{'name':'周金辉','phone':'13888279589'},{'name':'韩克军', 'phone':'15986783316'},
                  # {'name':'赖雪清', 'phone':'13823297263'},{'name':'杜文亚', 'phone':'18087113004'},{'name':'韦增涵','phone':'18776154224'},
                  # {'name':'黄曼丽', 'phone':'13427559800'},{'name':'陈奕宾','phone':'13544266987'},{'name':'王伟忠','phone':'18918028355'},
                  # {'name':'席啸', 'phone':'15342349300'},{'name':'吴胜', 'phone':'13812059957'},{'name':'邓其美', 'phone':'13856919766'},
                  # {'name':'黄秦拥', 'phone':'13923412278'},{'name':'艾光秀','phone':'15086708884'},{'name':'杨静','phone':'18674016521'},
                  {'name':'马艳萍', 'phone':'13759599909'}]
    return account_list


def getPhonelist(data):
    phone_list = []
    item = {}
    item["name"] = data["name"]
    item["check_name"]=None
    item["phone1"] = data["phone1"]
    try:
        phone_list.append(item)
        item = {}
        item["name"] = data["name"]
        item["check_name"] = None
        item["phone2"] = data["phone2"]
        phone_list.append(item)
    except:
        pass
    try:
        item = {}
        item["name"] = data["name"]
        item["check_name"] = None
        item["phone3"] = data["phone3"]
        phone_list.append(item)
        item = {}
    except:
        pass
    try:
        item["name"] = data["spouse_name"]
        item["check_name"] = None
        item["phone"] = data["spouse_phone1"]
        phone_list.append(item)
        item = {}
    except:
        pass
    try:
        item["name"] = data["spouse_name"]
        item["check_name"] = None
        item["phone"] = data["spouse_phone2"]
        phone_list.append(item)
        item = {}
    except:
        pass
    try:
        item["name"] = data["contact_name1"]
        item["check_name"] = None
        item["phone"] = data["contact_phone1"]
        phone_list.append(item)
        item = {}
    except:
        pass
    try:
        item["name"] = data["contact_name2"]
        item["check_name"] = None
        item["phone"] = data["contact_phone2"]
        phone_list.append(item)
        item = {}
    except:
        pass
    try:
        item["name"] = data["contact_name3"]
        item["check_name"] = None
        item["phone"] = data["contact_phone3"]
        phone_list.append(item)
        item = {}
    except:
        pass
    try:
        item["name"] = data["contact_name4"]
        item["check_name"] = None
        item["phone"] = data["contact_phone4"]
        phone_list.append(item)
        item = {}
    except:
        pass
    try:
        item["name"] = data["contact_name5"]
        item["check_name"] = None
        item["phone"] = data["contact_phone5"]
        phone_list.append(item)
        item = {}
    except:
        pass
    try:
        item["name"] = data["contact_name6"]
        item["check_name"] = None
        item["phone"] = data["contact_phone6"]
        phone_list.append(item)
        item = {}
    except:
        pass
    try:
        item["name"] = data["contact_name7"]
        item["check_name"] = None
        item["phone"] = data["contact_phone7"]
        phone_list.append(item)
        item = {}
    except:
        pass
    try:
        item["name"] = data["contact_name8"]
        item["check_name"] = None
        item["phone"] = data["contact_phone8"]
        phone_list.append(item)
        item = {}
    except:
        pass
    return phone_list
