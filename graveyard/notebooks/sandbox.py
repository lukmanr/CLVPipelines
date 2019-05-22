#%%

import json

dict = {'a': 1, 'b': 2}

json_dict = json.dumps(dict)

json.loads(json_dict)['a']