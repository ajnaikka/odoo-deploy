#! /bin/bash

ODOO_VERSION="$1"
PORT="$2"

PWD=$(pwd)
echo $HOME
PROJECT_PATH=$PWD
containerOdooRoot="/home/odoo/odoo"




rm -rf ansible/ Jenkinsfile docker-compose.yml odoo_pgpass

echo "deleted unwanted files"


mkdir src 
cd src
git clone -b $ODOO_VERSION --single-branch --depth=1 https://github.com/odoo/odoo.git

echo "cloned odoo repo"


# creating lauch config files

cd $PROJECT_PATH
mkdir .vscode 
cd .vscode

touch launch.json
touch settings.json
touch tasks.json

cat <<EOF > "launch.json"
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Docker Debug",
            "type": "docker",
            "request": "launch",

            // This is the task configuren
            "preLaunchTask": "odoo-debug",

            // remoteRoot is given as 
            // '/home/{odoo_user_name}/odoo' where odoo_user_name == odoo
            // Update it if you are using some other username in your image
            "python": {
                "pathMappings": [
                    {
                        "localRoot": "../",
                        "remoteRoot": "/home/odoo/odoo"
                    }
                ],
            },
        }
    ]
}
EOF

cat <<EOF > "settings.json"
// Place your settings in this file to overwrite default and user settings.
{
  
    // Odoo version. Put your project version here
    "odooVersion": "$ODOO_VERSION",
    // IMPORTANT: you need to update paths manually in lines 24 and 27 when changing version

    // Name of odoo user tat is used to run Odoo inside container
    "containerOdooUserName": "odoo",

    // Odoo root directory inside the container. This location is mounted to host file system
    "containerOdooRoot" : "home/odoo/odoo",
    
    // Odoo root directory on host. This directory will be mounted inside the container
    "hostOdooRoot" : "../",
    
    // use this so the autocompleate/goto definition will work with python extension
    "python.autoComplete.extraPaths": [
        "../src/odoo",  // Update this path when changing vesrion
    ],
    "python.analysis.extraPaths": [
        "../src/odoo",  // Update this path  when changing version
    ],
    "python.linting.enabled": true,

    //load the pylint_odoo
    // CHeck here for details: https://github.com/OCA/pylint-odoo
    "python.linting.pylintArgs": ["--load-plugins", "pylint_odoo"],
    "python.formatting.provider": "black",

    // add this auto-save option so the pylint will sow errors while editing otherwise
    //it will only show the errors on file save
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 500,

    // The following will hide the compiled file in the editor/ add other file to hide them from editor
    "files.exclude": {
        "**/*.pyc": true
    },
    "python.linting.flake8Enabled": false,
    "python.linting.pylintEnabled": true,
    "git.ignoreLimitWarning": true,

    // XML settings
    "xml.format.preserveEmptyContent": true,
    "xml.format.joinCDATALines": true,
    "xml.format.joinContentLines": true,
    "xmlTools.enableXmlTreeViewCursorSync": true,
    "xmlTools.splitXmlnsOnFormat": false,

    // Python type checking
    "python.analysis.typeCheckingMode": "basic",
}
EOF

cat <<EOF > "tasks.json"

// This configuration is provided as example
// You can use it as basis for your own custom config

// ******
// Configure variables in settings.json to implement your custom settings
// eg "odooVersion"
// *****
{
  "version": "2.0.0",
  "tasks": [

    // ******************************************
    // This configuration uses custom Dockerfile
    // Scroll to the botton to see how
    // to implement your own Dockerfile
    // ******************************************
    {
      // This label will be used in launch.json
      "label": "odoo-debug",
      "type": "docker-run",
      // Name of the task that is used to build image
      
      // This task will be run before running current task
      // Disable it to use pre-built image
      "dependsOn": ["build-image"],
      
      "dockerRun": {
        "containerName": "my-odoo-$ODOO_VERSION",          
        
        // Image name must be the same as image tag in the "docker-build" task
        "image": "my-odoo:$ODOO_VERSION",

        // containerPath is given as 
        // '/home/{odoo_user_name}/odoo' where odoo_user_name == odoo
        // Update it if you are using some other username in your image
        "volumes": [
          {
            "containerPath": "/home/odoo/odoo",
            "localPath": "$PROJECT_PATH"    //path where u clone the project repo
          },
          {
            "containerPath": "/var/lib/odoo",
            "localPath": "$HOME/postgres/varlib"  // varlib path with 777 permission
          }
        ],
        
        // This ports will be expos
        // If you want to run several Odoo instances at the same time
        // don't forget to assing different hostPort values to each of them
        "ports": [
          {
            "containerPort": 8069,
            "hostPort": $PORT
          },{
            "containerPort": 5678,
            "hostPort": 5678
          },
          // Activae this port only in case you need to lanuch Odoo in multi worker mode
          // {
          //   "containerPort": 8072,
          //   "hostPort": 8072
          // },
        ],
        
        // !!!!!!!!!!!!!!!!
        // This links container to specified Postgres container
        // It must be enabled in case you are not exposing port of your Postgres container
        // Eg you would like to use dedicated DB server for this project
       
        // "customOptions": "--link db-shared:db"

        // This option is needed to connect to the host port from withing the Docker container
        // Enable it if Postgres port is exposed to host
        "customOptions": "--add-host='host.docker.internal:host-gateway'"
      },

      // Argumetns that will be passed to Odoo executable
      // NB: all paths are given as "from inside the container"
      // Which meeans that if you move your config somethere else
      // you need to adjust the part of the path after 'home/odoo/odoo'
      "python": {
        "args": [
          // Odoo config file location
          "--config=$containerOdooRoot/config/odoo.conf",
          // ${config:containerOdooRoot}/
          // Uncomment the line below to Use selected DB only
          // "--database=my_odoo_db",
          // Uncomment the line below to automatically update the moduel(s)
          // "--update=my_odoo_module",
          // "--init=my_odoo_module",
          // "--test-enable",
          // "--stop-after-init",

        ],
        // Odoo binary executable
        "file": "$containerOdooRoot/src/odoo/odoo-bin"
        // ${config:containerOdooRoot}/
      },
    },
    // ***************************************
    // This task is used to build an image 
    //  from  Dockerfile
    // It will ve triggered only if "dependsOn": ["build-image"] is enabled in the upper task
    // ***************************************
    {
      "label": "build-image",
      "type": "docker-build",
      "dockerBuild": {
        // This pass is valid In case you cloned this repo to yout $HOME/odoo folder
        // Dont't forget to 
        "dockerfile": "$PROJECT_PATH/Dockerfile",   // path where u clone project repo+Dockerfile
        "context": "$PROJECT_PATH",  // path where u clone project repo
        // NB: tag must be the same as "image" field value in 
        "tag": "my-odoo:$ODOO_VERSION"
      }
    }
  ]
}
EOF

echo "created launch config files"


# changing conf file

cd $PROJECT_PATH/config

rm -rf odoo.conf

touch odoo.conf
cat <<EOF > "odoo.conf"
[options]
admin_passwd = loyaldebug
addons_path = /home/odoo/odoo/addons, /home/odoo/odoo/enterprise
list_db = True
proxy_mode = True
db_host = host.docker.internal
db_user = odoo
db_password = odoo
db_port = 5432
EOF

echo "odoo.conf file modified"
















