from datetime import date

from factory.alchemy import SQLAlchemyModelFactory
from factory import SubFactory, post_generation

from cache_registry import models
from instance.settings import FGAS


class OldCompanyLinkFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.OldCompanyLink
        sqlalchemy_session = models.db.session

    verified = True
    date_added = date(2015, 1, 1)
    date_verified = date(2015, 1, 1)


class OldCompanyFactory(SQLAlchemyModelFactory):

    class Meta:
        model = models.OldCompany
        sqlalchemy_session = models.db.session

    external_id = 10
    name = 'old_company_name'
    obligation = FGAS
    country_code = 'RO'
    account = 'account'
    vat_number = 'account'
    eori = 'account'
    active = True
    website = 'website'
    date_registered = date(2015, 1, 1)
    valid = True


class CountryFactory(SQLAlchemyModelFactory):

    class Meta:
        model = models.Country
        sqlalchemy_session = models.db.session

    code = 'c'
    name = 'n'
    type = 't'


class AddressFactory(SQLAlchemyModelFactory):

    class Meta:
        model = models.Address
        sqlalchemy_session = models.db.session

    country = SubFactory(CountryFactory)

    street = 's'
    number = 'n'
    city = 'c'
    zipcode = 'z'


class RepresentativeFactory(SQLAlchemyModelFactory):

    class Meta:
        model = models.EuLegalRepresentativeCompany
        sqlalchemy_session = models.db.session

    name = 'n'
    vatnumber = 'vat'
    contact_first_name = 'first'
    contact_last_name = 'last'
    contact_email = 'email'
    address = SubFactory(AddressFactory)


class BusinessProfileFactory(SQLAlchemyModelFactory):

    class Meta:
        model = models.BusinessProfile
        sqlalchemy_session = models.db.session


class UndertakingFactory(SQLAlchemyModelFactory):

    class Meta:
        model = models.Undertaking
        sqlalchemy_session = models.db.session

    external_id = 10
    name = 'n'
    website = 'w'
    phone = 'p'
    domain = FGAS
    status = 's'
    date_created = date(2015, 1, 1)
    date_updated = date(2015, 1, 1)
    undertaking_type = 'FGASUndertaking'
    vat = 'v'
    oldcompany_verified = True
    oldcompany_account = 'oldcompany_account'
    oldcompany_extid = 100
    address = SubFactory(AddressFactory)
    represent = SubFactory(RepresentativeFactory)
    oldcompany = SubFactory(OldCompanyFactory)

    @post_generation
    def contact_persons(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for cp in extracted:
                self.contact_persons.add(cp)

    @post_generation
    def types(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for type in extracted:
                self.types.add(type)

    @post_generation
    def represent_history(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for represent in extracted:
                self.represent_history.add(represent)

    @post_generation
    def businessprofiles(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for businessprofile in extracted:
                self.businessprofiles.add(businessprofile)


class TypeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.Type
        sqlalchemy_session = models.db.session

    domain = FGAS
    type = 'IMPORTER'


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.User
        sqlalchemy_session = models.db.session

    username = 'username'
    first_name = 'first'
    last_name = 'last'
    email = 'email@example.com'


class MatchingLog(SQLAlchemyModelFactory):
    class Meta:
        model = models.MatchingLog
        sqlalchemy_session = models.db.session


class OrganizationLog(SQLAlchemyModelFactory):
    class Meta:
        model = models.OrganizationLog
        sqlalchemy_session = models.db.session


class MailAddress(SQLAlchemyModelFactory):
    class Meta:
        model = models.MailAddress
        sqlalchemy_session = models.db.session

    mail = 'test@test.com'
    first_name = 'first_name'
    last_name = 'last_name'


class DeliveryLicenceFactory(SQLAlchemyModelFactory):

    year = 2019
    undertaking = SubFactory(UndertakingFactory)

    class Meta:
        model = models.DeliveryLicence
        sqlalchemy_session = models.db.session


class SubstanceFactory(SQLAlchemyModelFactory):

    year = 2019
    substance = 'Substance name (virgin)'
    lic_use_kind = 'Kind'
    lic_use_desc = 'Desc'
    lic_type = 'Export'
    quantity = 0.2
    deliverylicence = SubFactory(DeliveryLicenceFactory)

    class Meta:
        model = models.Substance
        sqlalchemy_session = models.db.session


class LicenceFactory(SQLAlchemyModelFactory):

    year =  2019
    chemical_name = 'Substance name'
    organization_country_name = 'US'
    organization_country_name_orig = 'USA'
    custom_procedure_name = 'substance'
    international_party_country_name = 'IT'
    international_party_country_name_orig = 'Italy'
    qty_qdp_percentage = 12
    qty_percentage = 3
    licence_state = 'VALID'
    long_licence_number = 4325
    template_detailed_use_code = 'substance'
    licence_type = '32'
    mixture_nature_type = 'virgin'
    substance = SubFactory(DeliveryLicenceFactory)


    class Meta:
        model = models.Licence
        sqlalchemy_session = models.db.session


class SubstanceNameConversionFactory(SQLAlchemyModelFactory):

    ec_substance_name = 'Substance name (virgin)'
    corrected_name = 'Substance name (virgin)'

    class Meta:
        model = models.SubstanceNameConversion
        sqlalchemy_session = models.db.session


class CountryCodesConversionFactory(SQLAlchemyModelFactory):
    __tablename__ = 'country_codes_conversion'

    country_name_short_en = 'USA'
    country_code_alpha2 = 'US'

    class Meta:
        model = models.CountryCodesConversion
        sqlalchemy_session = models.db.session


class LicenceDetailsConverstionFactory(SQLAlchemyModelFactory):
    __tablename__ = 'licence_details_conversion'

    template_detailed_use_code = 'substance'
    lic_use_kind = 'Kind'
    lic_use_desc = 'Desc'
    lic_type = 'Export'

    class Meta:
        model = models.LicenceDetailsConverstion
        sqlalchemy_session = models.db.session
