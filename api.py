from datetime import date, datetime
from typing import Annotated, Literal

from domain import ProviderName, Commodity
from domain.models.getup import Model
from domain.models.granularity import Granularity
from domain.models.points_price import PointsCountry, PointsCurrency
from domain.models.series import Series
from fastapi import APIRouter, Query
from infrastructure.adapters.fastapi_json_response_presenter import FastAPIJsonResponsePresenter

from application.api.dependencies.authenticate import use_authentication
from application.api.dependencies.state import WithUseCases


def authenticated(prefix: str):
    router = APIRouter(dependencies=[use_authentication()], prefix=prefix)

    @router.get("/series/day_ahead", response_model_exclude_none=True, tags=["Series", "Public"])
    def get_series_day_ahead_price(
        use_cases: WithUseCases,
        start: date = Query(
            description="inclusive lower bound",
            examples=["2022-01-01"],
            openapi_examples={"ex": {"value": "2022-01-01"}},
        ),
        end: date = Query(
            description="exclusive upper bound",
            examples=["2023-01-01"],
            openapi_examples={"ex": {"value": "2023-01-01"}},
        ),
        granularity: Granularity = Granularity.HOURLY,
        country: str = Query(),
        provider: ProviderName | None = None,
    ) -> Series[PointsCurrency]:
        response = FastAPIJsonResponsePresenter[Series[PointsCurrency]]()
        use_cases.series_day_ahead_price(
            start_date=start,
            end_date=end,
            country=country,
            granularity=granularity,
            presenter=response,
            provider=provider,
        )

        return response.value()

    @router.get("/series/forecasts", tags=["Series", "Public"])
    def get_prices_forecasts(
        use_cases: WithUseCases,
        country: str,
        model: Model,
        run_date: Annotated[date, Query(default_factory=datetime.now().date)],
        granularity: Literal[Granularity.DAILY, Granularity.HOURLY] = Granularity.HOURLY,
    ) -> Series[PointsCountry]:
        response = FastAPIJsonResponsePresenter[PointsCountry]()
        use_cases.series_getup_prices(
            country=country,
            model=model,
            run_date=run_date,
            granularity=granularity,
            presenter=response,
        )

        return response.value()

    @router.get("/futures/settlements", tags=["Series" ,"Public"])
    def get_futures_settlement_prices(
        use_cases: WithUseCases,
        commodity: Commodity,
        country: str,
        trading_date: date = Query(
            examples=["2023-01-01"],
            openapi_examples={"ex": {"value": "2023-01-01"}},
        ),
    ) -> Series[PointsCountry]:
        pass

    return router

