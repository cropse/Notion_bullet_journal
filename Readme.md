# Bullet journal generator

## requirement
python 3.6 above
## quick install
> pip install -r requirement
## quick start
1. duplicate the template from here
https://www.notion.so/cropse/Bullet-Journal-Template-7e32f801ee4d473db71e8aeb19634840
1. create `secret.yml` base on `secret_example.yml`, fill out secret according guide.
1. run ```python bullet_gen.py```, wail till see `have fun`

Note:
- support Link exist page, if there is `done` field inside page, it will supoort same logic as well.

### TODO:
- move incident to weekly event(kinda nice I guess?)
- async request to speed up
- commend line mode(for specify date you want)
- unittest maybe?
- video demonstration
- the function to add task to today?(command line)
