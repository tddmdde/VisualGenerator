from fastapi import APIRouter


# from .endpoints.urls import router as router_url
# from .endpoints.smm import router as router_smm
from .endpoints.home import router as router_home
# from .endpoints.seo import router as router_seo
# from .endpoints.analysis import router as router_analysis
# from .endpoints.direct import router as router_direct
# from .endpoints.custom import router as router_custom
# from .endpoints.content import router as router_content
# from .endpoints.promotion import router as router_promotion
# from .endpoints.visuals import router as router_visuals
# from .endpoints.map_events import router as router_map_events
# from .endpoints.map_events_edit_delete import app as router_map_events_edit_delete
# from .endpoints.segmentator import router as router_segmentator
# from .endpoints.bill_checker import router as router_bill_checker

router = APIRouter()

# router.include_router(router_home)
# router.include_router(router_url)
# router.include_router(router_smm)
# router.include_router(router_seo)
# router.include_router(router_analysis)
# router.include_router(router_direct)
# router.include_router(router_custom)
# router.include_router(router_content)
# router.include_router(router_promotion)
router.include_router(router_visuals)
# router.include_router(router_map_events)
# router.include_router(router_map_events_edit_delete)
# router.include_router(router_segmentator)
# router.include_router(router_bill_checker)