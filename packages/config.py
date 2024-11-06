import os

from pydantic_settings import BaseSettings
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from packages.handler import ModelHandler

path = os.path.abspath(os.getcwd())


class ProjectConfig(ModelHandler):
    def __init__(self, model_type="BERT"):
        super(ProjectConfig, self).__init__(
            yaml_path=os.path.join(path, "models", model_type, "config.yaml"),
        )
        self.model_type = model_type
        self.threshold = 0.5
        self.project_path = os.path.abspath(os.getcwd())


class VariableConfig:
    def __init__(self):
        self.host_list = ["127.0.0.1", "0.0.0.0"]
        self.port_list = ["8000", "8088"]


class APIEnvConfig(BaseSettings):
    host: str = Field(default="0.0.0.0", env="api host")
    port: int = Field(default="8000", env="api server port")

    # host 점검
    @validator("host", pre=True)
    def check_host(cls, host_input):
        if host_input == "localhost":
            host_input = "127.0.0.1"
        if host_input not in VariableConfig().host_list:
            raise ValueError("host error")
        return host_input

    # port 점검
    @validator("port", pre=True)
    def check_port(cls, port_input):
        if port_input not in VariableConfig().port_list:
            raise ValueError("port error")
        return port_input


class APIConfig(BaseModel):
    api_name: str = "main:app"
    api_info: APIEnvConfig = APIEnvConfig()


class DataInput(BaseModel):
    title: str = Field(..., title="News Title")
    content: str = Field(..., title="News Content")


class PredictOutput(BaseModel):
    prob: float
    prediction: str
