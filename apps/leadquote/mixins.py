import json
import requests


class LeadQuoteMixin(object):
    """

    """

    def is_valid_postal_code(self, zip_code):
        """
        set data into session.
        :param user:
        :return:
        """
        error = ''
        status = False
        json_zipcode_content = self.get_zipcode_json_content(zip_code)
        if json_zipcode_content.get('success'):
            status = True
        elif not json_zipcode_content.get('success'):
            status = False
            error = json_zipcode_content.get('message')
        return status, error

    def get_zipcode_countries(self, zip_code):
        """
        set data into session.
        :param user:
        :return:
        """
        json_zipcode_content = self.get_zipcode_json_content(zip_code)
        zip_counties = json_zipcode_content.get('data').get('locations')
        return zip_counties

    def get_zipcode_json_content(self, zip_code):

        """

        :return:
        """

        headers = {'content-type': 'application/json'}
        zipcode_response = requests.get("https://my.jewelersmutual.com/"
                                        "jewelry-insurance-quote-apply/api/PostalCode/{0}".format(zip_code),
                                        verify=False, headers=headers)
        if zipcode_response.status_code == 200:
            json_zipcode_content = json.loads(zipcode_response.content)
        else:
            json_zipcode_content = {}
        return json_zipcode_content

    def get_rating_json_content(self, jewellerydetailsformSet, customer):
        """

        :param zip_code:
        :return:
        """
        totalJewelryValue = 0
        jewellery_items = []
        for form in jewellerydetailsformSet:
            jewellery_price = form.cleaned_data.get('jewellery_price')
            jewellery = form.cleaned_data.get('jewellery')
            jewellery_item = self.get_rating_playload(jewellery, customer, jewellery_price)
            jewellery_items.append(jewellery_item)
            totalJewelryValue += int(jewellery_price)
        print "jewellery_items", jewellery_items

        headers = {'content-type': 'application/json'}
        playload = '{"accountLocation":{"ZipCode":"49534","County":"KENT",' \
                    '"State":"MI","Country":0},"effectiveDate":"2015-10-08",'\
                     '"jewelryItems":%s,"isPlatinumPoints":"false","jewelerCode":"",' \
                     '"emailAddress":"","isJewelersMutualCareTips":"false",'\
                    '"isJewelersMutualPolicyholder":"false",'\
                    '"riskModifiers":{"totalJewelryValue":%s,"safeType":"null",' \
                    '"safeConcealed":"false","safeAnchored":"false",' \
                    '"safeWeightClass":"null","alarmType":"null"}}'\
                    % (jewellery_items, totalJewelryValue)
        response = requests.post("https://my.jewelersmutual.com/jewelry-insurance-quote-apply/api/rating", data=playload, headers=headers,
                          verify=False)
        self.set_premium_content(json.loads(response.content))
        return json.loads(response.content)

    def get_rating_playload(self, jewellery, customer, jewellery_price):
        country_select = str(customer.country_select.encode('utf-8'))
        jewel_location = self.get_jewel_location(country_select, customer)
        jewellery_item = {"itemId":jewellery.id,
                         "jewelryLocation":jewel_location,"itemType":1,"itemValue":jewellery_price,"storedInSafe":"false"}

        return jewellery_item

    def get_jewel_location(self, country_select, customer):
        """

        :return:
        """
        import ast

        s = country_select.encode('utf-8')
        dis = ast.literal_eval(s)
        jewel_location = {}
        for k, v in dis.iteritems():
            key = k.encode('utf-8')
            try:
                val = int(v)
            except ValueError:
                val = v.encode('utf-8')
            jewel_location.update({key:val})
        jewel_location["ZipCode"] = str(customer.zip_code)
        return jewel_location

    def set_premium_content(self, content):
        """

        :param content:
        :return:
        """
        self.request.session['premium_content'] = content

    def get_premium_content(self):
        """

        :param content:
        :return:
        """
        premium_content = self.request.session['premium_content']
        return premium_content

    def get_initial_total_amt(self, premium_content):

        """

        :param premium_content:
        :return:
        """
        total = 0
        for jewelryItem in premium_content.get('jewelryItems'):
            premium = jewelryItem.get('premiums')[0]
            total += int(premium)
        return total
