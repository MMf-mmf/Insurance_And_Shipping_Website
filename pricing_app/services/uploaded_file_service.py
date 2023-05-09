import pandas as pd
from ..models import ShipmentFile, RateCardItem
from utils.helper_functions import get_ip_address
from django.utils import timezone
from io import BytesIO
from django.core.files.base import ContentFile
import chardet


######### file upload service ############
def handle_file_upload(request, file):
    if request.user.is_authenticated:
        # the file is saved like this because the file was losing data when uploaded to the cloud with  ShipmentFile.objects.create(file=file, user=request.user) 
        file.open()
        f = file.read()
        shipment = ShipmentFile(user=request.user)
        shipment.file.save(file.name, ContentFile(f))
        file.close()
        return shipment
    else:
        client_ip = get_ip_address(request)
        if client_ip is None:
            shipment = ShipmentFile.objects.create(file=file)
        else:
            # We got the client's IP address
            shipment = ShipmentFile.objects.create(file=file, ip_address=client_ip)
        return shipment
    

def file_felid_validations(request, file):
    base_df = pd.read_csv('static/files/shipmentsSample.csv')
    # GET THE FILE ENCODING TO AVOID ERRORS TRYING TO READ THE CSV WITH THE WRONG ENCODING
    file.open()
    file_bytes = file.read()
    encoding = chardet.detect(file_bytes)['encoding']
    uploaded_df = pd.read_csv(BytesIO(file_bytes), encoding=encoding)
    users_pricing_queryset = None
    errors = []
    
    
    #################### PRICE CALCULATION #############
    def start_adding_pricing():
        carrier_dvu = {}
        # if the user is logged in get his rate_card_tier
       
        if request.user.is_authenticated:
            users_tier = request.user.rate_card_tier
            # find the users active rate card
            users_pricing_queryset = RateCardItem.objects.filter(rate_card__tier_rank=users_tier, rate_card__expiration_date__gte=timezone.now())
        else:# if the user is not logged in use the default rate card (tier 1)
            users_pricing_queryset = RateCardItem.objects.filter(rate_card__tier_rank=1, rate_card__expiration_date__gte=timezone.now())
        # if there are no rate cards active for the user return a error message
        if users_pricing_queryset.exists() == False:
            return ['No Active Rate Card found, please contact customer support'] 
        for carrier in users_pricing_queryset:
            try:
                carrier_dvu[carrier.carrier] = carrier.cost_per_DVU
            except: 
                return ['There is no rate card for the user']
        # add column to called Price
       
        uploaded_df['Price'] = 0
        # loop over the dataFrame and calculate the price for each row
        for index, row in uploaded_df.iterrows():
            # establish the carrier
            carrier = uploaded_df.loc[index]['ShippingMethodSelected']
            dvu_for_carrier = carrier_dvu[carrier]
            # how much the customer wants to insure the package for
            declared_value = row['Value']
            # add the price of how much we are going to charge to insure the package
            cost = round((float(declared_value) / 100) * float(dvu_for_carrier), 2)
            uploaded_df.loc[index, 'Price'] = cost
        
        # as of now the file uploaded by the user is in the buffer as <InMemoryUploadedFile: shipmentsSample.csv (text/csv)>
        # what we can now do is write the new dataFrame to the buffer affectively swapping out the old file with the newly updated one.
        
        file.seek(0) # this is not the first time we are reading from the buffer (we read from it to create the dataFrame) now we need to set the place we want to start writing to the file.
        uploaded_df.to_csv(file, sep=',',header=True, index=False, mode='wb')
        return file


#################### VALIDATION and  ####################
    # final cell validation method (13)
    def validate_company_name():
        if uploaded_df['Shipper'].str.len().lt(25).all():
           pass
        else:
            errors.append('one or more company names is incorrect please reference the Sample file for a list of correct company names (please make sure the company name is less then 25 characters!)')
    # method (12)
    def validate_country():
        # validate country is less then 15 characters
        if uploaded_df['ShipCountry'].str.len().lt(30).all():
           
            validate_company_name()
        else:
            errors.append('one or more countries is incorrect please reference the Sample file for a list of correct customer countries (please make sure the country is less then 15 characters!)')
    # method (11)
    def validate_zip_code():
        # validate zip code is less then 15 characters
        if uploaded_df['ShipZipCode'].str.len().lt(15).all():
            validate_country() 
        else:
            errors.append("one or more zip codes are missing or are to long ( if the city you are shipping does not have have a zip code please input that country's zip equivalent  )")
    # method (10)
    def validate_state():
        # validate state is less then 15 characters
        
        if uploaded_df['ShipState'].str.len().lt(15).all():
            validate_zip_code() 
        else:
            errors.append('one or more states fields are missing if the destination does not have a state use the destinations name in place of state (please make sure the state is less then 15 characters!)')
    # method (9)
    def validate_city():
        # test str is less then 20 characters
        if uploaded_df['ShipCity'].str.len().lt(20).all():
          
            validate_state()
        else:
            errors.append('one or more cities is incorrect please reference the Sample file for a list of correct customer cities (please make sure the city is less then 20 characters!)')
    # method (8)
    def validate_customer_address():
        # test that the customer address is less then 50 characters
        if uploaded_df['ShipAddress1'].str.len().lt(50).all():
           
            validate_city()
        else:
            errors.append('one or more customer addresses is incorrect please reference the Sample file for a list of correct customer addresses (please make sure the customer address is less then 50 characters!)')

    # method (7)
    def validate_order_id():
        # convert order id to string
        uploaded_df['OrderID'] = uploaded_df['OrderID'].astype(str)
        # test that the ids are numbers and less then 20 numbers long
        if uploaded_df['OrderID'].str.isnumeric().all() and uploaded_df['OrderID'].str.len().lt(20).all():

            validate_customer_address()
        else:
            errors.append('one or more order ids is incorrect please reference the Sample file for a list of correct order ids')
    # method (6)        
    def validate_declared_value():
        #test that the dollar value is less then 10,000
        if uploaded_df['Value'].lt(10000).all():
          
            validate_order_id()
        else:
            errors.append('one or more declared values is incorrect please reference the Sample file for a list of correct declared values (please make sure the declared value is less then 10,000)')
    # method (5)
    def validate_tracking_number():
        # test that tracking number is les then 50 characters
        if uploaded_df['TrackingNumber'].str.len().lt(50).all():
       
            validate_declared_value()
        else:
            errors.append('one or more tracking numbers is incorrect please reference the Sample file for a list of correct tracking numbers (please make sure the tracking number is valid!)')
    # method (4)
    def carrier_service_exist():
        # test if the carrier services uploaded by the user exist in the sample file
        if uploaded_df['ShippingMethodSelected'].isin(base_df['ShippingMethodSelected']).all():
           
            validate_tracking_number()
        else:
            errors.append('one or more of the carrier services is incorrect please reference the Sample file for a list of correct carrier services')
    # method (3)
    def test_date():
        try:
            pd.to_datetime(uploaded_df['ShipDate'], format='%m/%d/%Y', errors='raise')
          
            carrier_service_exist()
        except ValueError:
            errors.append('ship date is incorrect please reference the Example file for correct Date format (date should be in month/day/year format)')  
    # method (2)          
    def is_columns_correct():
        if uploaded_df.columns.tolist() == base_df.columns.tolist():
            # test first column values to see if they are correct
            test_date()
        else:
            errors.append('columns are incorrect please reference the Example file for correct column names') 
    # method (1)  
    def start_file_validation_process():
        # start with testing the columns length
        if len(base_df.columns) == len(uploaded_df.columns):
            # Columns Length is correct now test if the columns names are correct
            is_columns_correct()
        else:
            errors.append('Columns Length is incorrect please reference the template file for the correct columns')
    # validate columns and values
    start_file_validation_process()
    # if errors in validation return errors else continue to add pricing column
    if len(errors)>0:
        return errors
    else:
        file_or_error = start_adding_pricing()
        return file_or_error
    


