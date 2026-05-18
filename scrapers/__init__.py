from scrapers.gma_news import GMANewsScraper
from scrapers.abs_cbn import ABSCBNScraper
from scrapers.cnn_ph import CNNPhilippinesScraper
from scrapers.inquirer import InquirerScraper
from scrapers.philippine_star import PhilippineStarScraper
from scrapers.manila_bulletin import ManilaBulletinScraper
from scrapers.rappler import RapplerScraper
from scrapers.senate import SenateScraper
from scrapers.house_of_reps import HouseOfRepsScraper
from scrapers.official_gazette import OfficialGazetteScraper

ALL_SCRAPERS = [
    GMANewsScraper,
    ABSCBNScraper,
    CNNPhilippinesScraper,
    InquirerScraper,
    PhilippineStarScraper,
    ManilaBulletinScraper,
    RapplerScraper,
    SenateScraper,
    HouseOfRepsScraper,
    OfficialGazetteScraper,
]
