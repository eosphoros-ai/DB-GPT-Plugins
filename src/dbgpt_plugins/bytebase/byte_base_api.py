import os

import requests
import json
import time
import datetime
import enum
import paramiko
from dotenv import load_dotenv

# only work for test, if you load current plugin in your project, please add related CONFIGs into you env variables.
load_dotenv("../../../.plugin_env")

# the bate_base service address.
BYTEBASE_DOMAIN = os.getenv("BYTE_BASE_DOMAIN", "xxx")

HOST_NAME = os.getenv("HOST_NAME", "xxx")
SSH_PORT = os.getenv("SSH_PORT", 22)
HOST_USER = os.getenv("HOST_USER", "root")
HOST_PASSWORD = os.getenv("HOST_PASSWORD", "xxx")

# you should copy the cookie from byte_base service, "f12" for windows, "command + shift + i" for mac
BB_COOKIE = os.getenv("BYTE_BASE_COOKIE", "xxx")

# create three database instance in different env, as the default instance to create, or operate database.
DEFAULT_INSTANCE_NAME_DEV = os.getenv("BYTE_BASE_DEFAULT_DEV_INSTANCE", "mysql_dev")
DEFAULT_INSTANCE_NAME_TEST = os.getenv("BYTE_BASE_DEFAULT_TEST_INSTANCE", "mysql_test")
DEFAULT_INSTANCE_NAME_PROD = os.getenv("BYTE_BASE_DEFAULT_PROD_INSTANCE", "mysql_prod")

# you should create a project named 'DB-GPT' in byte_base firstly.
DEFAULT_PROJECT_NAME = os.getenv("DEFAULT_PROJECT_NAME", "DB-GPT")

BB_DB_CREATE_URL = "/api/issue"
BB_DB_QUERY_URL = "/api/issue/{}"
BB_CREATE_SHEET_URL = "/api/sheet"
BB_INSTANCE_URL = "/api/instance"
BB_PROJECT_URL = "/api/project"
BB_DATABASE_URL = "/api/database"
BB_OVERVIEW_URL = BYTEBASE_DOMAIN + "/db"
BB_ISSUE_URL = BYTEBASE_DOMAIN + "/issue"
BB_DATABASE_DETAIL_PAGE_TEMPLATE = BYTEBASE_DOMAIN + "/db/{}-{}#overview"
ALLOWED_ENVIRONMENTS = {"dev", "test", "prod"}
BB_PING = "/api/sql/ping"
BB_CREATE_INSTANCE = "/api/instance"
BB_QUERY_SQL = "/api/sql/execute/admin"

class EnvEnum(enum.Enum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


def exec_ssh_command(command: str) -> str:
    """
    build a connection between client and server, then execute command, return the execution result.
    Args:
        command: such as 'ls ', 'docker ps', 'docker run -it ...'

    Returns:
        execute result.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST_NAME, SSH_PORT, HOST_USER, HOST_PASSWORD)
    stdin, stdout, stderr = client.exec_command(command)

    ret = stdout.read().decode()
    client.close()
    return ret


def deploy_mysql_server(port: str, password: str):
    """
    docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=123456 -p 3308:3306 -d mysql:latest

    Args:
        port: localhost port
        password: the password of root

    Returns:
        the result of deploy mysql server

    """
    docker_cmd = f"docker run --name mysql_{port} -e MYSQL_ROOT_PASSWORD={password} -p {port}:3306 -d mysql:latest"

    return exec_ssh_command(docker_cmd)


def create_database(database_name: str, env: str, description: str):
    """
    Create database by param CreateReq, and return Response.json
    Args:
        database_name: database name
        env: env (dev, test, prod)
        description: description of database

    Returns: the result information of create database.
    """
    url = BYTEBASE_DOMAIN + BB_DB_CREATE_URL

    if env.lower() not in ALLOWED_ENVIRONMENTS:
        return "please add environment information."

    labels = [{"key": "bb.environment", "value": env.lower()}]

    if env.lower() == "prod":
        instance_name = DEFAULT_INSTANCE_NAME_PROD
        instance_id = query_instance_id_by_name(DEFAULT_INSTANCE_NAME_PROD)
    elif env.lower() == "dev":
        instance_name = DEFAULT_INSTANCE_NAME_DEV
        instance_id = query_instance_id_by_name(DEFAULT_INSTANCE_NAME_DEV)
    else:
        instance_name = DEFAULT_INSTANCE_NAME_TEST
        instance_id = query_instance_id_by_name(DEFAULT_INSTANCE_NAME_TEST)

    if instance_id is None:
        raise ValueError(f"instance not exist, instance name is {instance_name}")

    project_id = query_project_by_name(DEFAULT_PROJECT_NAME)
    if project_id is None:
        raise ValueError(f"project not exist, project name is {DEFAULT_PROJECT_NAME}")

    user_id = get_user_from_cookie(BB_COOKIE)
    if user_id is None:
        raise ValueError(f"get user id failed. cookie={BB_COOKIE}")

    create_context = {
        "instanceId": int(instance_id),
        "databaseName": database_name,
        "tableName": "",
        "owner": "",
        "characterSet": "utf8mb4",
        "collation": "utf8mb4_general_ci",
        "cluster": "",
        "labels": json.dumps(labels),
    }

    request = {
        "data": {
            "type": "IssueCreate",
            "attributes": {
                "name": f"Create database '{database_name}'",
                "type": "bb.issue.database.create",
                "description": description,
                "assigneeId": 1,
                "projectId": int(project_id),
                "pipeline": {"stageList": [], "name": ""},
                "createContext": json.dumps(create_context),
                "payload": "{}",
            },
        }
    }
    response_json = post_json_data(url, request)
    return parse_create_result(response_json)


def create_table(database_name: str, env: str, statement: str):
    return update_schema(database_name, env, statement)


def create_index(database_name: str, env: str, statement: str):
    return update_schema(database_name, env, statement)


def delete_table(database_name: str, env: str, statement: str):
    return update_schema(database_name, env, statement)


def delete_index(database_name: str, env: str, statement: str):
    return update_schema(database_name, env, statement)


def execute_ddl(database_name: str, env: str, statement: str):
    return update_schema(database_name, env, statement)


def create_instance(
    db_type: str,
    instance_name: str,
    server_host: str,
    server_port: str,
    password: str,
    env: str,
):
    """
    create database instance.
    Args:
        db_type:
        instance_name:
        server_host:
        server_port:
        password:
        env:

    Returns:
        the result of create instance
    """
    env_id = None
    env_list = query_env_list()
    for p_env in env_list:
        if p_env["env_name"].lower() == env:
            env_id = p_env["env_id"]
            break

    if env_id is None:
        return f"current env {env} is not exist!"

    deploy_mysql_result = deploy_mysql_server(server_port, password)
    if not is_single_line_no_space(deploy_mysql_result):
        return f"create instance error: {deploy_mysql_result}"

    url = BYTEBASE_DOMAIN + BB_PING
    request_body = {
        "data": {
            "type": "connectionInfo",
            "attributes": {
                "id": -1,
                "resourceId": "",
                "rowStatus": "NORMAL",
                "name": instance_name,
                "engine": db_type.upper(),
                "environmentId": env_id,
                "host": server_host,
                "port": server_port,
                "username": "root",
                "password": password,
                "useEmptyPassword": False,
                "database": "",
                "srv": False,
                "authenticationDatabase": "",
                "sid": "",
                "serviceName": "",
                "sshHost": "",
                "sshPort": "",
                "sshUser": "",
                "sshPassword": "",
                "sshPrivateKey": "",
                "sslCa": "",
                "sslKey": "",
                "sslCert": "",
            },
        }
    }
    resp = post_json_data(url, request_body)
    if not (
        resp
        and resp["data"]
        and resp["data"]["attributes"]
        and resp["data"]["attributes"]["error"] == ""
    ):
        return f"ping {server_host}:{server_port} fail!"

    create_instance_url = BYTEBASE_DOMAIN + BB_CREATE_INSTANCE
    create_instance_body = {
        "data": {
            "type": "InstanceCreate",
            "attributes": {
                "resourceId": instance_name,
                "name": instance_name,
                "engine": db_type.upper(),
                "environmentId": env_id,
                "host": server_host,
                "port": server_port,
                "database": "",
                "username": "root",
                "password": password,
                "sslCa": "",
                "sslCert": "",
                "sslKey": "",
                "srv": False,
                "authenticationDatabase": "",
                "sid": "",
                "serviceName": "",
                "sshHost": "",
                "sshPort": "",
                "sshUser": "",
                "sshPassword": "",
                "sshPrivateKey": "",
            },
        }
    }

    resp = post_json_data(create_instance_url, create_instance_body)
    if (
        resp
        and resp["data"]
        and resp["data"]["id"]
        and resp["data"]["attributes"]
        and resp["data"]["attributes"]["name"]
    ):
        return f"create and bind instance {instance_name} success!"
    return f"create instance {instance_name} in host success, but bind instance fail: {resp}"


def create_project(project_name: str, project_key: str):
    """
    create project
    Args:
        project_name:
        project_key:

    Returns:

    """
    pass


def create_env(env_name: str, is_prod: str, public_strategy):
    """

    Args:
        env_name:
        is_prod:
        public_strategy:

    Returns:

    """
    pass


def execute_sql(database_name: str, env: str, statement: str):
    """

    Args:
        database:
        env_name:
        statement:

    Returns:

    """

    instance_name = None
    if env.lower() == EnvEnum.PROD.value:
        instance_name = DEFAULT_INSTANCE_NAME_PROD
    elif env.lower() == EnvEnum.TEST.value:
        instance_name = DEFAULT_INSTANCE_NAME_TEST
    if instance_name is None:
        return "instance is not found!"
    instance_id = query_instance_id_by_name(instance_name)

    url = BYTEBASE_DOMAIN + BB_QUERY_SQL
    request_body = {
        "data": {
            "type": "sqlExecute",
            "attributes": {
                "instanceId": int(instance_id),
                "databaseName": database_name,
                "statement": statement,
                "limit": 1000,
                "readonly": True,
            },
        }
    }
    resp = post_json_data(url, request_body)
    if (
        resp
        and resp["data"]
        and resp["data"]["attributes"]
        and (resp["data"]["attributes"]["error"] is None or resp["data"]["attributes"]["error"] == "")
    ):
        single_sql_result_list = resp["data"]["attributes"]["singleSQLResultList"]
        if (
            single_sql_result_list
            and len(single_sql_result_list) > 0
            and single_sql_result_list[0]["data"]
        ):
            json_data = json.loads(single_sql_result_list[0]["data"])
            ret = ""
            ret = ret + str(json_data[0]) + "\n"
            for data in json_data[2]:
                ret = ret + str(data) + "\n"
            return ret


def post_json_data(url: str, json_data: dict):
    """
    Submit a post request
    Args:
        url: http utl address
        json_data: the request data

    Returns: http response

    """
    response = requests.post(url, data=json.dumps(json_data), headers=get_auth_header())
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        return None


def get_with_header(url: str, headers: dict):
    """
    Send GET request with header
    Args:
        url:
        headers:

    Returns:

    """
    response = requests.get(url, headers=headers)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        return None


def get_auth_header():
    """
    Returns: auth info
    """
    headers = {
        "Cookie": BB_COOKIE,
        "Content-type": "application/json",
    }
    return headers


def parse_create_result(response_json):
    """
    Parse and query the status of creating database.
    Args:
        response_json: the response of create database.

    Returns:
        the result of create database

    """
    response_data = response_json["data"]
    issue_id = None
    if response_data and response_data.get("id"):
        issue_id = response_data["id"]
    if issue_id is not None:
        # query the status of creating database
        count = 0
        while True:
            query_json = get_with_header(
                BYTEBASE_DOMAIN + BB_DB_QUERY_URL.format(issue_id), get_auth_header()
            )
            if query_json and query_json["data"]:
                query_json_data = query_json["data"]
                if (
                    query_json_data
                    and query_json_data["attributes"]
                    and query_json_data["attributes"]["status"]
                ):
                    status = query_json_data["attributes"]["status"]
                    if status == "DONE":
                        return (
                            f"issue status is DONE, more detail see {BB_OVERVIEW_URL}"
                        )
                    elif status == "OPEN":
                        if query_json["included"]:
                            for step in query_json["included"]:
                                if (
                                    step["type"]
                                    and step["type"] == "taskRun"
                                    and step["attributes"]
                                    and step["attributes"]["status"]
                                    and step["attributes"]["status"] == "FAILED"
                                ):
                                    return f"create database failed, {step['attributes']['result']}"
                    else:
                        return f"issue status: {status}, please see {BB_OVERVIEW_URL}"
            time.sleep(1)
            count = count + 1
            if count > 2:
                break
    return f"create database timeout, please check in the bytebase service! more detail see: {BB_ISSUE_URL}"


def create_sheet(statement: str, database_name: str):
    """
    Create table sheet
    Args:
        statement: sql string / DDL string
        database_name: the database to operate DDL

    Returns:
        sheet id.
    """
    now = datetime.datetime.now()
    readable_time = now.strftime("%Y-%m-%d %H:%M:%S")

    project_id = query_project_by_name(DEFAULT_PROJECT_NAME)
    if project_id is None:
        raise ValueError(f"project not exist, project name is {DEFAULT_PROJECT_NAME}")

    request = {
        "data": {
            "type": "createSheet",
            "attributes": {
                "projectId": int(project_id),
                "name": f"[{database_name}] Alter schema {readable_time} - {database_name}",
                "statement": statement,
                "visibility": "PROJECT",
                "source": "BYTEBASE_ARTIFACT",
                "payload": "{}",
            },
        }
    }
    response_data = post_json_data(BYTEBASE_DOMAIN + BB_CREATE_SHEET_URL, request)
    if response_data and response_data["data"] and response_data["data"]["id"]:
        sheet_id = response_data["data"]["id"]
        if is_integer(sheet_id):
            return int(sheet_id)
    return None


def get_database_id_by_name(database_name: str, env: str, project_id: str):
    """
    Query database id by database name.
    Args:
        database_name:
        env: (dev, test, prod)
        project_id: project, default using #{DEFAULT_PROJECT_NAME}

    Returns:
        database id of current database(env, instance_id, database_name)

    """
    database_id = None
    database_list = query_databases(env)
    for db in database_list:
        if (
            db["database_name"]
            and db["database_name"] == database_name
            and db["project_id"] == int(project_id)
        ):
            database_id = int(db["database_id"])
            break
    return database_id


def create_issue(sheet_id: int, database_name: str, aim_env: str):
    """
    Execute create table by sheet_id

    Args:
        sheet_id:
        database_name:
        aim_env:

    Returns:
        issue id when created.
    """
    database_id = get_database_id_by_name(
        database_name, aim_env, query_project_by_name(DEFAULT_PROJECT_NAME)
    )
    now = datetime.datetime.now()
    readable_time = now.strftime("%Y-%m-%d %H:%M:%S")

    project_id = query_project_by_name(DEFAULT_PROJECT_NAME)
    if project_id is None:
        raise ValueError(f"project not exist, project name is {DEFAULT_PROJECT_NAME}")

    user_id = get_user_from_cookie(BB_COOKIE)
    if user_id is None:
        raise ValueError(f"get user id failed. cookie={BB_COOKIE}")

    create_context = {
        "detailList": [
            {
                "migrationType": "MIGRATE",
                "databaseId": database_id,
                "statement": "",
                "sheetId": sheet_id,
                "earliestAllowedTs": 0,
            }
        ]
    }
    request = {
        "data": {
            "type": "IssueCreate",
            "attributes": {
                "projectId": int(project_id),
                "name": f"[{database_name}] Alter schema {readable_time} - {database_name}",
                "type": "bb.issue.database.schema.update",
                "description": "",
                "assigneeId": user_id,
                "createContext": json.dumps(create_context),
                "payload": "{}",
            },
        }
    }
    response_data = post_json_data(BYTEBASE_DOMAIN + BB_DB_CREATE_URL, request)
    if response_data and response_data["data"] and response_data["data"]["id"]:
        return response_data["data"]["id"]
    return None


def get_create_table_result(issue_id: str, database_name: str, aim_env: str):
    """
    Query issue status by issue_id

    Args:
        issue_id:
        database_name:
        aim_env:

    Returns:
        The result of create table / execute DDL

    """
    database_address = BB_DATABASE_DETAIL_PAGE_TEMPLATE.format(
        database_name,
        get_database_id_by_name(
            database_name, aim_env, query_project_by_name(DEFAULT_PROJECT_NAME)
        ),
    )
    if not issue_id:
        return {"status": "failed", "msg": "the issue is not exist!"}
    response_data = get_with_header(
        BYTEBASE_DOMAIN + BB_DB_QUERY_URL.format(issue_id), get_auth_header()
    )
    if (
        response_data
        and response_data["data"]
        and response_data["data"]["attributes"]
        and response_data["data"]["attributes"]["status"]
    ):
        create_table_status = response_data["data"]["attributes"]["status"]
        if "DONE" == create_table_status:
            return {
                "status": "success",
                "msg": "update schema success! " + database_address,
            }
        elif "OPEN" == create_table_status:
            if response_data["included"]:
                for step in response_data["included"]:
                    if (
                        step["type"]
                        and step["type"] == "taskRun"
                        and step["attributes"]
                        and step["attributes"]["status"]
                        and step["attributes"]["status"] == "FAILED"
                    ):
                        return {
                            "status": "failed",
                            "msg": "update schema failed, "
                            + step["attributes"]["result"]
                            + database_address,
                        }
        else:
            return {
                "status": "failed",
                "msg": f"update schema status={create_table_status}! {database_address}",
            }
    return {"status": "running", "msg": "the issue is running. " + database_address}


def update_schema(database_name: str, env: str, statement: str):
    """
    create table, can split as three steps:
        1. createSheet;
        2.IssueCreate
        3. GET Create Table Status
    Args:
        database_name:
        env:
        statement:

    Returns:
        The result of create table / execute ddl
    """
    sheet_id = create_sheet(statement, database_name)
    if not sheet_id:
        return "create sheet failed !"
    issue_id = create_issue(sheet_id, database_name, env)
    if not issue_id:
        return "create task failed, the issue is not exist!"
    count = 0
    while True:
        create_result = get_create_table_result(issue_id, database_name, env)
        if create_result and create_result["status"] == "success":
            return create_result["msg"]
        elif create_result and create_result["status"] == "failed":
            return create_result["msg"]
        time.sleep(1)
        count = count + 1
        if count > 2 or env.lower() == "prod":
            break
    return f"update schema timeout! please skip to url: {BB_ISSUE_URL}"


def is_integer(s):
    """
    Decide the param 's' an integer type
    Args:
        s:

    Returns:
    """

    try:
        int(s)
        return True
    except ValueError:
        return False


def query_instance_list():
    """
    Query all instance
    Returns:
        the instance list.
    """
    response_data = get_with_header(
        BYTEBASE_DOMAIN + BB_INSTANCE_URL, get_auth_header()
    )
    instance_list = []
    if response_data and response_data["data"]:
        for instance in response_data["data"]:
            if (
                instance["type"]
                and instance["type"] == "instance"
                and instance["attributes"]
                and instance["attributes"]["name"]
            ):
                instance_list.append(
                    {
                        "instance_id": instance["id"],
                        "instance_name": instance["attributes"]["name"],
                    }
                )
    return instance_list


def query_instance_list_by_env(env_str: str):
    """
    query instance by env
    Args:
        env_str: dev, test, prod

    Returns:
        the instance list when env is specified.
    """
    response_data = get_with_header(
        BYTEBASE_DOMAIN + BB_INSTANCE_URL, get_auth_header()
    )
    instance_list = []

    required_env_id = None
    if response_data and response_data["included"]:
        for env in response_data["included"]:
            if (
                env["type"]
                and env["type"] == "environment"
                and env["attributes"]
                and env["attributes"]["name"]
                and env["attributes"]["name"].lower() == env_str.lower()
            ):
                required_env_id = env["id"]
    print(
        f"query_instance_list_by_env(): required_env={env_str}, required_env_id={required_env_id}"
    )

    if response_data and response_data["data"]:
        for instance in response_data["data"]:
            if instance["type"] and instance["type"] == "instance":
                if (
                    instance["relationships"]
                    and instance["relationships"]["environment"]
                    and instance["relationships"]["environment"]["data"]
                    and instance["relationships"]["environment"]["data"]["type"]
                    == "environment"
                ):
                    if (
                        instance["relationships"]["environment"]["data"]["id"]
                        == required_env_id
                    ):
                        instance_list.append(
                            {
                                "instance_id": instance["id"],
                                "instance_name": instance["attributes"]["name"],
                            }
                        )
    return instance_list


def query_env_list():
    """
    query env list
    Returns:
        env list
    """
    env_list = []
    response_data = get_with_header(
        BYTEBASE_DOMAIN + BB_INSTANCE_URL, get_auth_header()
    )
    if response_data and response_data["included"]:
        for env in response_data["included"]:
            if env["type"] and env["type"] == "environment":
                env_list.append(
                    {"env_id": env["id"], "env_name": env["attributes"]["name"]}
                )
    return env_list


def query_project_list():
    project_list = []
    response_data = get_with_header(BYTEBASE_DOMAIN + BB_PROJECT_URL, get_auth_header())

    if response_data and response_data["data"]:
        for project in response_data["data"]:
            if (
                project["type"]
                and project["type"] == "project"
                and project["attributes"]
                and project["attributes"]["name"]
            ):
                project_list.append(
                    {
                        "project_id": project["id"],
                        "project_name": project["attributes"]["name"],
                    }
                )
    return project_list


def query_project_by_name(project_name: str):
    """
    query project with a default value.
    Args:
        project_name:

    Returns:
        project id by name

    """
    project_list = query_project_list()
    for proj in project_list:
        if proj["project_name"].lower() == project_name.lower():
            return proj["project_id"]
    return None


def query_instance_id_by_name(instance_name: str):
    """
    query instance id by name
    Args:
        instance_name:

    Returns:

    """
    instance_list = query_instance_list()
    for ins in instance_list:
        if ins["instance_name"].lower() == instance_name.lower():
            return ins["instance_id"]
    return None


def query_databases(aim_env: str):
    """
    Query database by env
    Args:
        aim_env:

    Returns:
        the databases when env is specified.

    """
    database_list = []
    response_data = get_with_header(
        BYTEBASE_DOMAIN + BB_DATABASE_URL, get_auth_header()
    )
    if response_data and response_data["data"]:
        for database in response_data["data"]:
            labels = json.loads(database["attributes"]["labels"])
            env_name = None
            for label in labels:
                if (
                    label["key"]
                    and label["key"] == "bb.environment"
                    and label["value"]
                    and aim_env.lower() == label["value"].lower()
                ):
                    env_name = label["value"]
                    break
            database_list.append(
                {
                    "database_name": database["attributes"]["name"],
                    "instance_id": database["attributes"]["instanceId"],
                    "project_id": database["attributes"]["projectId"],
                    "database_id": database["id"],
                    "env_name": env_name,
                }
            )
    return database_list


def get_user_from_cookie(cookie: str):
    """
    get user id from cookie.
    Args:
        cookie:

    Returns:

    """
    tokens = cookie.split(";")
    for token in tokens:
        if token.__contains__("="):
            sub_tokens = token.split("=")
            if sub_tokens[0].strip() == "user":
                return int(sub_tokens[1].strip())
    return None


def is_single_line_no_space(s):
    lines = s.split("\n")

    return len(lines) == 1 and lines[0].count(" ") == 0


###################################################################################
#  test create database by bytebase  ##################################
# ret = create_database("xy-gpt", "test", "database for test puiposes")
# print(ret)


###################################################################
#  test create table by bytebase  ##################################
# statement = """
#         CREATE TABLE `pz_job` (
#             `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
#             `gmt_create` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
#             `gmt_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
#             `job_id` varchar(100) NOT NULL COMMENT '任务id',
#             `job_name` varchar(1000) NOT NULL DEFAULT '' COMMENT '任务名称',
#             `job_type` varchar(255) NOT NULL COMMENT '任务类型',
#             `job_mode` varchar(100) NOT NULL COMMENT '任务模式',
#             `content` text DEFAULT NULL COMMENT '任务参数',
#             `pre_time` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '上次执行时间',
#             `next_time` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '下次执行时间',
#             `job_interval` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '时间间隔',
#             `instance` varchar(50) DEFAULT '' COMMENT '指定运行实例',
#             `status` varchar(50) NOT NULL DEFAULT '' COMMENT '任务状态',
#             PRIMARY KEY (`id`)
#         ) AUTO_INCREMENT = 1001 DEFAULT CHARSET = utf8mb4;
#     """

# statement = "CREATE INDEX idx_job_type ON pz_job_v15(job_type);"
# create_table_result = create_table("xygpt2", 'test', statement)
# print("create result ==========" + json.dumps(create_table_result))

#
# envlist = query_env_list()
# print(envlist)

# execute sql test ##############################################################
# result = execute_sql("dbgpt_shine", "prod", "select * from t_job limit 1000;\n")

# result = execute_sql("dbgpt_shine", "prod", """
# INSERT INTO t_job (id, name, owner, status, gmt_create, gmt_modify)
# VALUES (100, 'Job 1', 'Owner 1', 'Pending', NOW(), NOW()),
#        (101, 'Job 2', 'Owner 2', 'In Progress', NOW(), NOW()),
#        (102, 'Job 3', 'Owner 3', 'Completed', NOW(), NOW()),
#        (103, 'Job 4', 'Owner 4', 'Pending', NOW(), NOW()),
#        (104, 'Job 5', 'Owner 5', 'In Progress', NOW(), NOW());
# """)
#
#
# result = execute_sql("dbgpt_shine", "prod", """
# delete from t_job where id = 105;
# """)
#
# print(result)
