from urlparse import urljoin
from celery.task import task
from celery.utils.log import get_task_logger
from django.conf import settings
import requests
from lxml import etree

from exchange.core.models import CSWRecord

logger = get_task_logger(__name__)


@task
def create_new_csw(record_id):
    """
    Attempt to create a new CSW record in Registry
    """
    csw_record_template = """
        <csw:Transaction xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
        xmlns:ows="http://www.opengis.net/ows"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2
        http://schemas.opengis.net/csw/3.0.0/CSW-publication.xsd"
        service="CSW" version="2.0.2"
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:dct="http://purl.org/dc/terms/"
        xmlns:registry="http://gis.harvard.edu/HHypermap/registry/0.1" >
        <csw:Insert>

            <csw:Record>
            <dc:identifier>{uuid}</dc:identifier>
            <dc:title>{title}</dc:title>
            <dc:creator>{creator}</dc:creator>
            <dc:type>{record_type}</dc:type>
            <dct:alternative>{alternative}</dct:alternative>
            <dct:modified>{modified}</dct:modified>
            <dct:abstract>{abstract}</dct:abstract>
            <dc:format>{record_format}</dc:format>
            <dc:source>{source}</dc:source>
            <dc:relation>{relation}</dc:relation>
            <dc:gold>{gold}</dc:gold>
            <dc:category>{category}</dc:category>
            <registry:property
            name="ContactInformation/Primary/organization"
            value="{contact}" />
            <ows:BoundingBox
            crs="http://www.opengis.net/def/crs/EPSG/0/4326"
            dimensions="2">
                <ows:LowerCorner>{bbox_l}</ows:LowerCorner>
                <ows:UpperCorner>{bbox_u}</ows:UpperCorner>
            </ows:BoundingBox>
            </csw:Record>

        </csw:Insert>
        </csw:Transaction>"""

    namespaces = {
        "csw": "http://www.opengis.net/cat/csw/2.0.2",
        "dc": "http://purl.org/dc/elements/1.1/",
        "ows": "http://www.opengis.net/ows",
    }

    record = CSWRecord.objects.get(id=record_id)
    record.status = "Pending"
    record.save()

    registry_url = settings.REGISTRYURL
    catalog = settings.REGISTRY_CAT
    csw_url = urljoin(registry_url, "catalog/{}/csw".format(catalog))
    post_data = csw_record_template.format(uuid=record_id,
                                           title=record.title,
                                           creator=record.creator,
                                           record_type=record.record_type,
                                           alternative=record.alternative,
                                           modified=record.modified,
                                           abstract=record.abstract,
                                           record_format=record.record_format,
                                           source=record.source,
                                           relation=record.relation,
                                           gold=record.gold,
                                           category=record.category,
                                           contact=record.contact_information,
                                           bbox_l=record.bbox_lower_corner,
                                           bbox_u=record.bbox_upper_corner,
                                           )

    logger.info("Creating new CSW with: \n{}".format(post_data))
    response = requests.post(csw_url, data=post_data)

    if response.status_code != 200:
        record.status = "Error"
        record.save()
        logger.error("{} during CSW record creation: {}".format(
            response.status_code,
            response.content))
        return

    parsed = etree.fromstring(response.content)
    exceptiontext = parsed.xpath("//ows:ExceptionText",
                                 namespaces=namespaces)
    totalinserted = parsed.xpath("//csw:totalInserted",
                                 namespaces=namespaces)

    if exceptiontext:
        # we're going to consider this an "error" even if registry returns a
        # positive TransactionSummary/totalInserted value along with the error
        record.status = "Error"
        record.save()
        for x in exceptiontext:
            logger.error("Error during record creation: {}".format(x.text))
        return

    if totalinserted > 0:
        record.status = "Complete"
        record.save()
        logger.info("Record successfully created: {}".format(response.content))
        return
