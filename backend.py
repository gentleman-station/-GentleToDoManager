from random import randint
from utils import APP_ROOT_DIR
from montydb import set_storage, MontyClient


DATABASE_PATH = f"{APP_ROOT_DIR}/database"
DATABASE_NAME = "db"


set_storage(
    repository=DATABASE_PATH,
    storage="flatfile",
    use_bson=False,
    cache_modified=0
); db_client = MontyClient(DATABASE_PATH)
database = db_client[DATABASE_NAME]
task_collection = database.tasks


class ApplyDotNotation(dict):
    def __init__(self, *args, **kwargs):
        """
        Make dict values accessible using dot key(s).
        """
        super(ApplyDotNotation, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(ApplyDotNotation, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(ApplyDotNotation, self).__delitem__(key)
        del self.__dict__[key]


def _gen_random_id() -> int:
    random_id = randint(11111, 99999)
    for last_tasks in get():
        if random_id == last_tasks["_id"]:
            random_id =  randint(11111, 99999)
    return random_id


def add(task: str) -> dict:
    task_object = {"_id": _gen_random_id(), "name": task, "completed": False}
    task_collection.insert_one(task_object)
    return ApplyDotNotation(task_object)


def remove(task_id: int) -> bool:
    try:
        del_obj = task_collection.delete_one({"_id": task_id})
    except Exception:
        return False
    return bool(del_obj)


def edit(task_id: int, task: str, completion: bool) -> dict:
    task_collection.update_one({"_id": task_id}, {"$set": {"name": task, "completed": completion}})
    return {"_id": task_id, "name": task, "completed": completion}


def get(filter: dict = {}) -> list:
    tasks = []
    for task_info in task_collection.find(filter):
        tasks.append(ApplyDotNotation(task_info))
    return tasks


def reload_db():
    global db_client, database, task_collection
    db_client = MontyClient(DATABASE_PATH)
    database = db_client[DATABASE_NAME]
    task_collection = database.tasks