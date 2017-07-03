import os
import re


lst = ['consumer%3A%2F%2F172.31.10.200%2Fcom.born.keap.shop.order.service.IKeapOrderService%3Fapplication%3Dkeap_dubbo-client%26category%3Dconsumers%26check%3Dfalse%26dubbo%3D2.8.3%26interface%3Dcom.born.keap.shop.order.service.IKeapOrderService%26methods%3DmdyOrderSendedInvoice%2CmodifyOrderInsuranceInfo%2CqueryHolderAndInsuredInfo%2CcancelOrder%2CqueryOrders%2CdelayedOrder%2CsaveOrderMemos%2CqueryOrderDetail%2CgetOrderMdyDetail%2CqueryOrder'
       , 'consumer%3A%2F%2F172.31.10.240%2Fcom.born.keap.shop.order.service.IKeapOrderService%3Fapplication%3Dkeap_dubbo-client%26category%3Dconsumers%26check%3Dfalse%26dubbo%3D2.8.3%26interface%3Dcom.born.keap.shop.order.service.IKeapOrderService%26methods%3DmdyOrderSendedInvoice%2CmodifyOrderInsuranceInfo%2CqueryHolderAndInsuredInfo%2CcancelOrder%2CqueryOrders%2CdelayedOrder%2CsaveOrderMemos%2CqueryOrderDetail%2CgetOrderMdyDetail%2CqueryOrder']
print(len(lst))
for x in lst:
    #consumers_ip = re.search('([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])', x)
    consumers_ip = re.search('(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])', x)
    print(consumers_ip.group(0))

