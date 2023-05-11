import requests
from tqdm import tqdm
from utils import write_to_csv

cookies = {
    '__lhash_': '77839d085660ef9f1919e1094cdb6284',
    'MVID_ACTOR_API_AVAILABILITY': 'true',
    'MVID_BLACK_FRIDAY_ENABLED': 'true',
    'MVID_CART_AVAILABILITY': 'true',
    'MVID_CATALOG_STATE': '1',
    'MVID_CITY_ID': 'CityCZ_31740',
    'MVID_CREDIT_AVAILABILITY': 'true',
    'MVID_CREDIT_SERVICES': 'true',
    'MVID_CRITICAL_GTM_INIT_DELAY': '3000',
    'MVID_FILTER_CODES': 'true',
    'MVID_FILTER_TOOLTIP': '1',
    'MVID_FLOCKTORY_ON': 'true',
    'MVID_GEOLOCATION_NEEDED': 'true',
    'MVID_GIFT_KIT': 'true',
    'MVID_GLC': 'true',
    'MVID_GLP': 'true',
    'MVID_GTM_ENABLED': '011',
    'MVID_INTERVAL_DELIVERY': 'true',
    'MVID_IS_NEW_BR_WIDGET': 'true',
    'MVID_KLADR_ID': '5000000100000',
    'MVID_LAYOUT_TYPE': '1',
    'MVID_LP_SOLD_VARIANTS': '3',
    'MVID_MCLICK': 'true',
    'MVID_MINDBOX_DYNAMICALLY': 'true',
    'MVID_MINI_PDP': 'true',
    'MVID_NEW_ACCESSORY': 'true',
    'MVID_NEW_LK_CHECK_CAPTCHA': 'true',
    'MVID_NEW_LK_OTP_TIMER': 'true',
    'MVID_NEW_MBONUS_BLOCK': 'true',
    'MVID_PROMO_CATALOG_ON': 'true',
    'MVID_REGION_ID': '1',
    'MVID_REGION_SHOP': 'S002',
    'MVID_SERVICES': '111',
    'MVID_TIMEZONE_OFFSET': '3',
    'MVID_TYP_CHAT': 'true',
    'MVID_WEB_SBP': 'true',
    'SENTRY_ERRORS_RATE': '0.1',
    'SENTRY_TRANSACTIONS_RATE': '0.5',
    '__utmz': '142257390.1682718374.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)',
    '_ym_uid': '1599049065768130797',
    '_ym_d': '1682718380',
    '__SourceTracker': 'google__organic',
    'admitad_deduplication_cookie': 'google__organic',
    'gdeslon.ru.__arc_domain': 'gdeslon.ru',
    'gdeslon.ru.user_id': '2b2d65a2-7d8e-4425-b007-cb553a47a0ec',
    'tmr_lvid': '06a9b259cdf4275e228626222bb306b6',
    'tmr_lvidTS': '1599049084550',
    'advcake_track_id': 'e71019ab-5423-693b-7c68-ee25735d3969',
    'advcake_session_id': '420a6bd4-585a-a44c-46ad-a492b426a576',
    'flocktory-uuid': '4679166e-5a9e-498c-991c-f8cd6f3b456e-8',
    'uxs_uid': '1f893610-e60e-11ed-bb94-9fa2978f8ffa',
    'adrcid': 'AqioJwCLLuRpJW_kt-q-G3Q',
    'afUserId': '134487a0-4389-46b7-847d-62fb238f2827-p',
    'AF_SYNC': '1682718385752',
    '_gid': 'GA1.2.1723441713.1682940985',
    'cookie_ip_add': '62.217.189.132',
    'MVID_GUEST_ID': '22493309539',
    'MVID_VIEWED_PRODUCTS': '',
    'wurfl_device_id': 'generic_web_browser',
    'MVID_CALC_BONUS_RUBLES_PROFIT': 'false',
    'NEED_REQUIRE_APPLY_DISCOUNT': 'true',
    'MVID_CART_MULTI_DELETE': 'false',
    'PROMOLISTING_WITHOUT_STOCK_AB_TEST': '2',
    'MVID_GET_LOCATION_BY_DADATA': 'DaData',
    'PRESELECT_COURIER_DELIVERY_FOR_KBT': 'true',
    'HINTS_FIO_COOKIE_NAME': '2',
    'searchType2': '2',
    'COMPARISON_INDICATOR': 'false',
    'MVID_NEW_OLD': 'eyJjYXJ0IjpmYWxzZSwiZmF2b3JpdGUiOnRydWUsImNvbXBhcmlzb24iOnRydWV9',
    'MVID_OLD_NEW': 'eyJjb21wYXJpc29uIjogdHJ1ZSwgImZhdm9yaXRlIjogdHJ1ZSwgImNhcnQiOiB0cnVlfQ==',
    '__zzatgib-w-mvideo': 'MDA0dC0cTHtmcDhhDHEWTT17CT4VHThHKHIzd2UwRGUmaExiKEdeUGshC1E0NWYQSk9NRw03QF43V2EgDBYRTVZTei0iFXhvKE8QE1s5Mzw0bXN4XCYKGlQ1XxlDak4NaTdsFzx1ZS8JMSxieTFSLxNLbD9HfDBILjQiDEJtNiRvL0tAZW9sKWIcOWMRdhgdOWA5UhINTRQZL3x/CyczYHFtZHVOe2NrbwxJPBpLFitnaSEfdz5CMRtBC2VGYBVgPzRSUH0uIhR4bSlTcAxhRUN2dytAax9oS2ERP0cVNmdcSkI3FVlLTShyPV8/YngiD2lIXydFXlF7Kh8XeXQqS3FSHAl5CDpodiZSUVElYRASSWtpYlE0XS1BR0cUdn85MHF/V2o0FmV6Yg==',
    '__zzatgib-w-mvideo': 'MDA0dC0cTHtmcDhhDHEWTT17CT4VHThHKHIzd2UwRGUmaExiKEdeUGshC1E0NWYQSk9NRw03QF43V2EgDBYRTVZTei0iFXhvKE8QE1s5Mzw0bXN4XCYKGlQ1XxlDak4NaTdsFzx1ZS8JMSxieTFSLxNLbD9HfDBILjQiDEJtNiRvL0tAZW9sKWIcOWMRdhgdOWA5UhINTRQZL3x/CyczYHFtZHVOe2NrbwxJPBpLFitnaSEfdz5CMRtBC2VGYBVgPzRSUH0uIhR4bSlTcAxhRUN2dytAax9oS2ERP0cVNmdcSkI3FVlLTShyPV8/YngiD2lIXydFXlF7Kh8XeXQqS3FSHAl5CDpodiZSUVElYRASSWtpYlE0XS1BR0cUdn85MHF/V2o0FmV6Yg==',
    'deviceType': 'desktop',
    'cfidsgib-w-mvideo': 'CvXo2PILult4CA+iHxw8joNUjj2tn2RoRd/30Pne6UfS06dsoAhqkXnX2FVJO0vzHZ42bSXdcG2GW4jIzL6JZlnFCC6TCBu57qsURiddhSz1RtdOjTqKWrSKWftDPVjuBQht1pzR1ldPOMKYMwhk39XLzmnO53nz6W0i',
    'cfidsgib-w-mvideo': 'CvXo2PILult4CA+iHxw8joNUjj2tn2RoRd/30Pne6UfS06dsoAhqkXnX2FVJO0vzHZ42bSXdcG2GW4jIzL6JZlnFCC6TCBu57qsURiddhSz1RtdOjTqKWrSKWftDPVjuBQht1pzR1ldPOMKYMwhk39XLzmnO53nz6W0i',
    'gsscgib-w-mvideo': 'wCKdvIz4DNPrQcqK6yLJpMioYfR8vU2lh7R4x1lqV+6YI+/moOOVOs2xsuZ/2G/HmyzYO02VeAD5+u0KTxVubndzhq3jJyiaf24nE78WZGC9dWOKIQSO+H1pK5c9XBDzbuPnFJu2wONBxHg6qeGfFfKZYXSCrNnPcDP9li0k3iw37VkGoh126nwoyL7N4IHZDrk7a2RAoWKNfDeo3goAn1+E0flHUgGi7xrRvyp3mIt3aTXAZgi4dOkCOqxfIQ==',
    'gsscgib-w-mvideo': 'wCKdvIz4DNPrQcqK6yLJpMioYfR8vU2lh7R4x1lqV+6YI+/moOOVOs2xsuZ/2G/HmyzYO02VeAD5+u0KTxVubndzhq3jJyiaf24nE78WZGC9dWOKIQSO+H1pK5c9XBDzbuPnFJu2wONBxHg6qeGfFfKZYXSCrNnPcDP9li0k3iw37VkGoh126nwoyL7N4IHZDrk7a2RAoWKNfDeo3goAn1+E0flHUgGi7xrRvyp3mIt3aTXAZgi4dOkCOqxfIQ==',
    'fgsscgib-w-mvideo': 'hqdl7537d0858ce3571e4cac8d481c9aa46364a7',
    'fgsscgib-w-mvideo': 'hqdl7537d0858ce3571e4cac8d481c9aa46364a7',
    'cfidsgib-w-mvideo': 'Q0AczvdzTftlobPVh1ik05YapuqgmTGVGLFXiDk1DralkRFAo2rpRbthebGovFXCibp4fYWMkBL7bVj46cYQkMW4DiroGc/zS4sJcSRJNV134SFUhqPsqRMqQZo5RgWmGPKipnDH4ILu5LANQlDjxvzOwM1Mo1Kt5LWd',
    'MVID_ENVCLOUD': 'prod1',
    '__utmc': '142257390',
    'MVID_COOKIE': '2500',
    '_ym_isad': '2',
    '_ga': 'GA1.2.2012810638.1682718374',
    '_ga_CFMZTSS5FM': 'GS1.1.1683021556.7.1.1683021580.0.0.0',
    '_ga_BNX5WPP3YK': 'GS1.1.1683021557.7.1.1683021580.37.0.0',
    '_sp_id.d61c': '89945daa-ff7b-4cf1-970b-bec368cfd4a3.1682718380.6.1683021711.1682980056.385e014d-9ceb-4b53-b7de-072139248559.0d68f93a-ef95-4137-b973-d4d08440fc41.62f23fb8-9e62-49bb-b2c4-ed79d4899108.1683018772819.22',
    'tmr_detect': '0%7C1683021717075',
    '__hash_': '09adc8ddd8efa27820c7c6262f95385c',
    '__utma': '142257390.2012810638.1682718374.1683018763.1683023528.6',
    '__utmt': '1',
    '__utmb': '142257390.1.10.1683023528',
}

headers = {
    'authority': 'www.mvideo.ru',
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9,en-RU;q=0.8,en;q=0.7,el-GR;q=0.6,el;q=0.5,en-US;q=0.4',
    # 'cookie': '__lhash_=77839d085660ef9f1919e1094cdb6284; MVID_ACTOR_API_AVAILABILITY=true; MVID_BLACK_FRIDAY_ENABLED=true; MVID_CART_AVAILABILITY=true; MVID_CATALOG_STATE=1; MVID_CITY_ID=CityCZ_31740; MVID_CREDIT_AVAILABILITY=true; MVID_CREDIT_SERVICES=true; MVID_CRITICAL_GTM_INIT_DELAY=3000; MVID_FILTER_CODES=true; MVID_FILTER_TOOLTIP=1; MVID_FLOCKTORY_ON=true; MVID_GEOLOCATION_NEEDED=true; MVID_GIFT_KIT=true; MVID_GLC=true; MVID_GLP=true; MVID_GTM_ENABLED=011; MVID_INTERVAL_DELIVERY=true; MVID_IS_NEW_BR_WIDGET=true; MVID_KLADR_ID=5000000100000; MVID_LAYOUT_TYPE=1; MVID_LP_SOLD_VARIANTS=3; MVID_MCLICK=true; MVID_MINDBOX_DYNAMICALLY=true; MVID_MINI_PDP=true; MVID_NEW_ACCESSORY=true; MVID_NEW_LK_CHECK_CAPTCHA=true; MVID_NEW_LK_OTP_TIMER=true; MVID_NEW_MBONUS_BLOCK=true; MVID_PROMO_CATALOG_ON=true; MVID_REGION_ID=1; MVID_REGION_SHOP=S002; MVID_SERVICES=111; MVID_TIMEZONE_OFFSET=3; MVID_TYP_CHAT=true; MVID_WEB_SBP=true; SENTRY_ERRORS_RATE=0.1; SENTRY_TRANSACTIONS_RATE=0.5; __utmz=142257390.1682718374.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _ym_uid=1599049065768130797; _ym_d=1682718380; __SourceTracker=google__organic; admitad_deduplication_cookie=google__organic; gdeslon.ru.__arc_domain=gdeslon.ru; gdeslon.ru.user_id=2b2d65a2-7d8e-4425-b007-cb553a47a0ec; tmr_lvid=06a9b259cdf4275e228626222bb306b6; tmr_lvidTS=1599049084550; advcake_track_id=e71019ab-5423-693b-7c68-ee25735d3969; advcake_session_id=420a6bd4-585a-a44c-46ad-a492b426a576; flocktory-uuid=4679166e-5a9e-498c-991c-f8cd6f3b456e-8; uxs_uid=1f893610-e60e-11ed-bb94-9fa2978f8ffa; adrcid=AqioJwCLLuRpJW_kt-q-G3Q; afUserId=134487a0-4389-46b7-847d-62fb238f2827-p; AF_SYNC=1682718385752; _gid=GA1.2.1723441713.1682940985; cookie_ip_add=62.217.189.132; MVID_GUEST_ID=22493309539; MVID_VIEWED_PRODUCTS=; wurfl_device_id=generic_web_browser; MVID_CALC_BONUS_RUBLES_PROFIT=false; NEED_REQUIRE_APPLY_DISCOUNT=true; MVID_CART_MULTI_DELETE=false; PROMOLISTING_WITHOUT_STOCK_AB_TEST=2; MVID_GET_LOCATION_BY_DADATA=DaData; PRESELECT_COURIER_DELIVERY_FOR_KBT=true; HINTS_FIO_COOKIE_NAME=2; searchType2=2; COMPARISON_INDICATOR=false; MVID_NEW_OLD=eyJjYXJ0IjpmYWxzZSwiZmF2b3JpdGUiOnRydWUsImNvbXBhcmlzb24iOnRydWV9; MVID_OLD_NEW=eyJjb21wYXJpc29uIjogdHJ1ZSwgImZhdm9yaXRlIjogdHJ1ZSwgImNhcnQiOiB0cnVlfQ==; __zzatgib-w-mvideo=MDA0dC0cTHtmcDhhDHEWTT17CT4VHThHKHIzd2UwRGUmaExiKEdeUGshC1E0NWYQSk9NRw03QF43V2EgDBYRTVZTei0iFXhvKE8QE1s5Mzw0bXN4XCYKGlQ1XxlDak4NaTdsFzx1ZS8JMSxieTFSLxNLbD9HfDBILjQiDEJtNiRvL0tAZW9sKWIcOWMRdhgdOWA5UhINTRQZL3x/CyczYHFtZHVOe2NrbwxJPBpLFitnaSEfdz5CMRtBC2VGYBVgPzRSUH0uIhR4bSlTcAxhRUN2dytAax9oS2ERP0cVNmdcSkI3FVlLTShyPV8/YngiD2lIXydFXlF7Kh8XeXQqS3FSHAl5CDpodiZSUVElYRASSWtpYlE0XS1BR0cUdn85MHF/V2o0FmV6Yg==; __zzatgib-w-mvideo=MDA0dC0cTHtmcDhhDHEWTT17CT4VHThHKHIzd2UwRGUmaExiKEdeUGshC1E0NWYQSk9NRw03QF43V2EgDBYRTVZTei0iFXhvKE8QE1s5Mzw0bXN4XCYKGlQ1XxlDak4NaTdsFzx1ZS8JMSxieTFSLxNLbD9HfDBILjQiDEJtNiRvL0tAZW9sKWIcOWMRdhgdOWA5UhINTRQZL3x/CyczYHFtZHVOe2NrbwxJPBpLFitnaSEfdz5CMRtBC2VGYBVgPzRSUH0uIhR4bSlTcAxhRUN2dytAax9oS2ERP0cVNmdcSkI3FVlLTShyPV8/YngiD2lIXydFXlF7Kh8XeXQqS3FSHAl5CDpodiZSUVElYRASSWtpYlE0XS1BR0cUdn85MHF/V2o0FmV6Yg==; deviceType=desktop; cfidsgib-w-mvideo=CvXo2PILult4CA+iHxw8joNUjj2tn2RoRd/30Pne6UfS06dsoAhqkXnX2FVJO0vzHZ42bSXdcG2GW4jIzL6JZlnFCC6TCBu57qsURiddhSz1RtdOjTqKWrSKWftDPVjuBQht1pzR1ldPOMKYMwhk39XLzmnO53nz6W0i; cfidsgib-w-mvideo=CvXo2PILult4CA+iHxw8joNUjj2tn2RoRd/30Pne6UfS06dsoAhqkXnX2FVJO0vzHZ42bSXdcG2GW4jIzL6JZlnFCC6TCBu57qsURiddhSz1RtdOjTqKWrSKWftDPVjuBQht1pzR1ldPOMKYMwhk39XLzmnO53nz6W0i; gsscgib-w-mvideo=wCKdvIz4DNPrQcqK6yLJpMioYfR8vU2lh7R4x1lqV+6YI+/moOOVOs2xsuZ/2G/HmyzYO02VeAD5+u0KTxVubndzhq3jJyiaf24nE78WZGC9dWOKIQSO+H1pK5c9XBDzbuPnFJu2wONBxHg6qeGfFfKZYXSCrNnPcDP9li0k3iw37VkGoh126nwoyL7N4IHZDrk7a2RAoWKNfDeo3goAn1+E0flHUgGi7xrRvyp3mIt3aTXAZgi4dOkCOqxfIQ==; gsscgib-w-mvideo=wCKdvIz4DNPrQcqK6yLJpMioYfR8vU2lh7R4x1lqV+6YI+/moOOVOs2xsuZ/2G/HmyzYO02VeAD5+u0KTxVubndzhq3jJyiaf24nE78WZGC9dWOKIQSO+H1pK5c9XBDzbuPnFJu2wONBxHg6qeGfFfKZYXSCrNnPcDP9li0k3iw37VkGoh126nwoyL7N4IHZDrk7a2RAoWKNfDeo3goAn1+E0flHUgGi7xrRvyp3mIt3aTXAZgi4dOkCOqxfIQ==; fgsscgib-w-mvideo=hqdl7537d0858ce3571e4cac8d481c9aa46364a7; fgsscgib-w-mvideo=hqdl7537d0858ce3571e4cac8d481c9aa46364a7; cfidsgib-w-mvideo=Q0AczvdzTftlobPVh1ik05YapuqgmTGVGLFXiDk1DralkRFAo2rpRbthebGovFXCibp4fYWMkBL7bVj46cYQkMW4DiroGc/zS4sJcSRJNV134SFUhqPsqRMqQZo5RgWmGPKipnDH4ILu5LANQlDjxvzOwM1Mo1Kt5LWd; MVID_ENVCLOUD=prod1; __utmc=142257390; MVID_COOKIE=2500; _ym_isad=2; _ga=GA1.2.2012810638.1682718374; _ga_CFMZTSS5FM=GS1.1.1683021556.7.1.1683021580.0.0.0; _ga_BNX5WPP3YK=GS1.1.1683021557.7.1.1683021580.37.0.0; _sp_id.d61c=89945daa-ff7b-4cf1-970b-bec368cfd4a3.1682718380.6.1683021711.1682980056.385e014d-9ceb-4b53-b7de-072139248559.0d68f93a-ef95-4137-b973-d4d08440fc41.62f23fb8-9e62-49bb-b2c4-ed79d4899108.1683018772819.22; tmr_detect=0%7C1683021717075; __hash_=09adc8ddd8efa27820c7c6262f95385c; __utma=142257390.2012810638.1682718374.1683018763.1683023528.6; __utmt=1; __utmb=142257390.1.10.1683023528',
    'referer': 'https://www.mvideo.ru/products/televizor-grundig-50-gfu-7800b-10031216',
    'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'x-kl-ajax-request': 'Ajax_Request',
}

params = {
    'categoryId': '65',
    'offset': '0',
    'limit': '24',
    'filterParams': 'WyJ0b2xrby12LW5hbGljaGlpIiwiLTEyIiwiZGEiXQ==',
    'doTranslit': 'true',
}
offset = 0
all_ids = []

# while offset <= 874:
#     try:
#         print(offset)
#         url = f'https://www.mvideo.ru/bff/products/listing'
#         params['offset'] = offset
#         # session.max_redirects = 100
#         response = requests.get(url,params=params, cookies=cookies,headers=headers)
#         # print(response.text)
#         data = response.json() # ,headers = headers, cookies=cookies
#         ids = data['body']['products']
#         print(len(ids))
        
#         with open('mvideo_ids.txt','a') as f:
#             f.write(','.join(ids))
#         all_ids.extend(ids)
#         offset += 24
#     except Exception as e:
#         print(offset)
#         print(e)
#     # break
# with open('mvideo_all_ids.txt','a') as f:
#         f.write(','.join(all_ids))
# print(len(all_ids))
with open('mvideo_all_ids.txt','r') as f:
    ids = f.read()
all_ids = ids.split(',')
all_ids = all_ids[595:]

for id in tqdm(all_ids):
    price_url = f'https://www.mvideo.ru/bff/products/prices?productIds={id}&isPromoApplied=true&addBonusRubles=true'
    info_url = f'https://www.mvideo.ru/bff/product-details?productId={id}'
    try:
        price_resp = requests.get(price_url, headers=headers, cookies=cookies)
        price = price_resp.json()['body']['materialPrices'][0]['price']['salePrice']

        info_resp = requests.get(info_url,headers=headers,cookies=cookies)
        data = info_resp.json()

        specs = {}
        for title in data['body']['properties']['all']:
            for spec in title['properties']:
                specs[spec['name']] = spec['value']

        product = {
            'id_on_store': id,
            'title': data['body']['name'],
            'brand': data['body']['brandName'],
            'price': price,
            'description': data['body']['description'],
            'specifications': specs,
            'category': 'TV',
            'marketplace':'mvideo',
            'url': 'https://www.mvideo.ru/products/' + data['body']['nameTranslit'] + '-' + id,
        }
        write_to_csv(product,'data/mvideo_TV.csv')
    except Exception as e:
        print(id)
        print(e)


# цены
# https://www.mvideo.ru/bff/products/prices?productIds=10030415&isPromoApplied=true&addBonusRubles=true

# вся остальная инфа
# https://www.mvideo.ru/bff/product-details?productId=10030415