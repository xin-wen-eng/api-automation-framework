# coding=utf-8
"""
    @project: pytest-auto-api2
    @blogs: https://blog.csdn.net/weixin_43865008
"""
from utils.mysql_tool.mysql_control import MysqlDB
import copy


class AddressDetection(MysqlDB):

    def get_shop_address_entity_str(self):
        """
        Get all shop addresses that are online and not deleted (excluding self-operated shops, which have no addresses)
        :return:
        """
        shop_info = self.query("SELECT id, name, attribute, shop_type, sub_shop_type "
                               "FROM `test_obp_supplier`.`supplier_shop` "
                               "where status = 2 and delete_flag = 0 and sub_shop_type > 300 "
                               "and sub_shop_type = 300")
        return shop_info

    def get_logistics_address_library(self):
        """
        Get the province codes from the platform address library
        :return:
        """

        code = self.query("select name, code from `test_obp_order`.`logistics_address_library` "
                          "where parent_code > 0")

        area_code = {}
        for i in code:
            area_code[i['code']] = i['name']
        return area_code

    def get_error_shop(self):
        """
        Get shop data with errors
        :return:
        """
        # Get area code
        get_logistics_address_library = self.get_logistics_address_library()
        num = 0
        for i in self.get_shop_address_entity_str():
            # Get shop address
            shop_address_entity_str = eval(i['attribute'])['shopAddressEntityStr']

            if shop_address_entity_str['countiesName'] == get_logistics_address_library[str(shop_address_entity_str['countiesCode'])]:
                pass
            else:
                area_name = self.query(f"SELECT name, code FROM `test_obp_order`.`logistics_address_library`"
                           f" where parent_code = {shop_address_entity_str['cityCode']} and name = '{shop_address_entity_str['countiesName']}'")
                num += 1

                new_shop_address_entity_str = copy.deepcopy(shop_address_entity_str)
                new_shop_address_entity_str['countiesCode'] = area_name[0]['code']
                # print(str(f'update obp_supplier.supplier_shop set attribute = json_set(attribute,"$.shopAddressEntityStr.countiesCode",{area_name[0]["code"]}) where id = {i["id"]};'))
                print(f"Shop name: {i['name']}, Shop id: {i['id']}, "
                      f"Shop address: {shop_address_entity_str['cityName']}{shop_address_entity_str['provinceName']}{shop_address_entity_str['countiesName']}"
                      f"\nCurrent actual data: {shop_address_entity_str}"
                      f"\nActual code for {shop_address_entity_str['countiesName']} is {area_name}"
                      f"\nUpdated data: {new_shop_address_entity_str}")
                print("*" * 100)


        print(num)


AddressDetection().get_error_shop()
