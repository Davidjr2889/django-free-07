## Installation steps

1- Make sure you have the following installed:

- Brew if you are using mac (https://brew.sh/)
- A python compiler (3.9.17)
- Node version 16.x
- pnpm installed
- Docker
- a makefile compliant cli (it is possible without it, but you'll have to manually run the commands inside the makefile)
- pnpm version 8+

2- Copy `./LBARM/.env.example` to `./LBARM/.env`.
Also Copy `./backoffice-vue/.env.development.local.example` to `./backoffice-vue/.env.development.local`. Make adjustments to the env vars if you are not happy with them.

3- Clone the repo https://github.com/pbgc/django-jwt-auth anywhere in your filesystem (ideally one level up) and make a symlink to it at the root level (do not clone inside the project to avoid git conflicts).
For UNIX systems (MAC/Linux):

```bash
    ln -s ../django-jwt-auth/jwt_auth .
```

> For Windows systems follow the steps in: https://woshub.com/create-symlink-windows/ to create the symlink

4- create virtual env and install the dependencies:
UNIX

```bash
    python -m venv env

    source ./env/bin/activate

    pip install -r reqs.txt
```

> In Windows:
>
> ```bash
>    python -m venv env
>
>    .\env\Scripts\activate.bat
>
>    pip install -r reqs.txt
> ```

WARNING: in windoes, if you run into problems during the installation, download the appropriate [python-ldap wheel](https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-ldap) and isntall manually. You will need to update this dependency in the reqs.txt file, run the `pip install -r reqs.txt` command and then discard changes to the file so that this dependency won't be upgraded accidentally.
NOTE: Side-effects of this hack is still unknown

Obs: To start the virtual environment after:

```bash
    source ./env/bin/activate
```

> In Windows:
>
> ```bash
>    .\env\Scripts\activate.bat
> ```

5- Setup the database with the provided seed (make sure Docker 4+ is installed):

```bash
    make set-db # this command can also be used to reset a db
    make setup
```

> In Windows:
>
> ```bash
> 	docker-compose --env-file ./LBARM/.env -p cia_espirituosa up --build -d
>
>    python .\manage.py migrate
> ```

6- Make a super user to be able to login to the admin panel.
The user is `user`. the password will be prompted for you to create

```bash
    make superuser
```

> In Windows:
>
> ```bash
>    python .\manage.py createsuperuser --username user --email user@email.com
> ```

7- Switch to the `./backoffice-vue/` directory and install node depedendencies using `pnpm`:

```bash
    pnpm install

    # This will fix module not found for vue-awesome
    cp ../Icon.vue ./node_modules/vue-awesome/components/Icon.vue
```

> In Windows:
>
> ```bash
>    pnpm install
> ```
>
> Then manuall copy the `Icon.vue` in the root folder into `./node_modules/vue-awesome/components/` folder.

8- Execute the backoffice with `pnpm serve` in the `./backoffice-vue/` directory

9- In a separate shell run the API server with `make server`

> In Windows:
>
> ```bash
>   python .\manage.py runserver
> ```

10- Login to the admin panel and create a user to access the backoffice
login with credentials created above

```bash
    http://localhost:8000/admin
```

Tips: Choose something easy for user/password. that is local and not production. don't go too hard on credential security.

# Unknwons

mudar pyrightconfig.json (se for usado este LSP)
