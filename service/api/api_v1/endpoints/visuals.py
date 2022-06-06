import json

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status, Form, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse

from service.core.logic.logic_system import get_current_username, check_role_paths, no_access_html, pth
from service.core.logic.logic_visuals import generate_html_markup_for_visuals, get_data_from_sku, generate_visual, \
    get_html_form_template, post_to_telegram

from service.core.models.input import VisualsCheckIN, VisualsGenerateIN, VisualsPostToTgIN
from service.core.models.output import VisualsCheckOUT, VisualsGenerateOUT, VisualsTemplateOUT

import inspect
import base64

router = APIRouter()
security = HTTPBasic()


@router.get('/visuals', response_class=HTMLResponse, tags=['VISUALS Operator'])
async def show_visuals_interface(request: Request, credentials: HTTPBasicCredentials = Depends(get_current_username)):
    """
    Function generates the HTML markup from input model. Ugly, but it works.
    """

    if not check_role_paths(router.url_path_for(inspect.stack()[0][3]), credentials):
        return no_access_html

    return await generate_html_markup_for_visuals(credentials, request)


@router.post('/visuals/get_data_from_sku', response_model=VisualsCheckOUT, tags=['VISUALS Operator'])
async def ask_for_data_sku(input: VisualsCheckIN, credentials: HTTPBasicCredentials = Depends(get_current_username)):
    """
    Function generates the HTML markup from input model. Ugly, but it works.
    """

    if not check_role_paths(router.url_path_for(inspect.stack()[0][3]), credentials):
        return no_access_html

    return await get_data_from_sku(credentials, input)


@router.post('/visuals/generate', response_model=VisualsGenerateOUT, tags=['VISUALS Operator'])
async def generate(input: VisualsGenerateIN, credentials: HTTPBasicCredentials = Depends(get_current_username)):
    """
    Function generates the HTML markup from input model. Ugly, but it works.
    """

    if not check_role_paths(router.url_path_for(inspect.stack()[0][3]), credentials):
        return no_access_html

    return await generate_visual(credentials, input)


@router.get('/visuals/templates/{template_id}', response_class=HTMLResponse, tags=['VISUALS Operator'])
async def get_form_template(template_id: str, credentials: HTTPBasicCredentials = Depends(get_current_username)):
    """
    Function returns HTML form template according to template_id
    """

    if not check_role_paths('/visuals/templates', credentials):
        return no_access_html

    return await get_html_form_template(template_id)


@router.get('/visuals/get_templates', response_model=VisualsTemplateOUT, tags=['VISUALS Operator'])
async def get_form_template(credentials: HTTPBasicCredentials = Depends(get_current_username)):
    """
    Function returns HTM    L form template according to template_id
    """

    if not check_role_paths(router.url_path_for(inspect.stack()[0][3]), credentials):
        return no_access_html

    to_return = {
        "data": [
            {
                "value": "basic",
                "text": "Товарка Базовая"
            },
            {
                "value": "2_events",
                "text": "Товарка с Двумя Событиями"
            }
        ]
    }

    return to_return


@router.post('/visuals/post_to_tg', tags=['VISUALS Operator'])
async def post_to_tg(input: VisualsPostToTgIN, credentials: HTTPBasicCredentials = Depends(get_current_username)):

    if not check_role_paths(router.url_path_for(inspect.stack()[0][3]), credentials):
        return no_access_html

    await post_to_telegram(input)