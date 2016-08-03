import requests

playload = {"accountLocation":{"ZipCode":"49534","County":"KENT","State":"MI","Country":0},
            "effectiveDate":"2015-10-08","jewelryItems":[{"itemId":1,
            "jewelryLocation":{"ZipCode":"49534","County":"KENT","State":"MI","Country":0},
            "itemType":1,"itemValue":5500,"storedInSafe":False}],"isPlatinumPoints":False,
            "jewelerCode":"","emailAddress":"","isJewelersMutualCareTips":False,
            "isJewelersMutualPolicyholder":False,"riskModifiers":{"totalJewelryValue":5500,
            "safeType":None,"safeConcealed":False,"safeAnchored":False,"safeWeightClass":None,"alarmType":None}}

r = requests.post("https://my.testjewelersmutual.com/jewelry-insurance-quote-apply/api/rating", data=playload,
                  verify=False)
print "rrrrrrrrrrrrrrrrrrrrr", r.content