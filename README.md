# clopper - cloud integrated extension of [hopper](https://github.com/sealuzh/hopper)
Clopper is an extension of [hopper](https://github.com/sealuzh/hopper) a tool to mine performance history of benchmark and unit tests. It is designed to run in parallel using multiple remote instances. To do so, the provided test suite is splitted, distributed among the remote instances and hopper-execution triggered. The instances continuously store the results to a (google) cloud bucket storage. In the end, the local host will gather the results and concatenate them to a single output file.

# System requirements
* Python 2.7
* Python packages (use pip to install them):
    * paramiko
	* scp
    * grpcio and grpcio-tools
    * git
    * untangle
    * [pygit2](http://www.pygit2.org/install.html) and its requirements
    * google-cloud storage

# Preparation
* Visit [Google Cloud Platform](https://console.cloud.google.com/project), create a new project and enable billing (there is a free trial available including credit of $300 for a year).
* In Google's [storage-console](https://console.cloud.google.com/storage/), create a new bucket. Note down its name (e.g. "clopper-storage").
* Visit Google's [API-console](https://console.cloud.google.com/apis/credentials) and establish a new service account key: > Create credentials > Service Account key > Select default service account > json-format (default) > Create. These are the credentials for the cloud storage bucket. Download the json-file and store it in a secure place. Note down the file path. 
* Create a number of desired instances on a cloud-platform of your choice or use a group of remote computers. Note down their IP-addresses and optionally their names. Please use Ubuntu 16.04 LTS as operating system on your instances.
* Generate a new SSH key for your instances. Choose the name to use on the instances (most likely you hostname). Note down the file path of the key and make sure the key is not publicly readable (run "$ chmod 400 /path/to/ssh-key-file" to restrict access). If you use cloud-instances, this can be done on the cloud-platform. If you use remote instances, use "$ ssh-keygen -t rsa" and copy the keys to your remote computers with "$ ssh-copy-id -i /the-new-ssh-key-file USER@IP" replacing USER with your name on the instances and IP with the remote machine's IP address (see also [this](https://askubuntu.com/questions/4830/easiest-way-to-copy-ssh-keys-to-another-machine/4833#4833) or [that](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2) page).
* Prepare the project to mine as specified by [hopper](https://github.com/sealuzh/hopper). Put the project and the benchmarks into seperate folders and store them in a directory. Note down the path of this parent-directory. It should match the following structure:


        ├── parent-directory            
        │   ├── git project          
        │   ├── jmh-root dir         # the jmh-root dir containing the benchmarks  


* Prepare an xml-config file, as specified by [hopper](https://github.com/sealuzh/hopper). Note down the file path.
* Prepare a json-config file including the fields:
    * total: the total number of remote instances.
    * ip-list: a dictionary of the form {instance-name : ip} of the remote instances. Instance-name must end with a hyphen and a unique number of max. 2 digits length (e.g. instance-01, instance-02, instance-03).
    * project: the path of the project-directory containing the jmh-root dir and the git-project (see structure above).
    * username: Add, if your username is different than the name used on the system, defaults to $USER. The username must match with the one of the SSH-key.
    * distribution: the splitting method which is used to distribute the versions and tests. Choose one of the following:
        * VersionDistributor: to split by version-ranges
        * RandomVersionDistributor: to assign each instance a selection of random versions.
        * TestDistributor: to split randomly among all available tests (unit or benchmarks)
        * VersionTestDistributor: to split by version ranges and randomly by tests
        * RandomDistributor: to split completely randomly: random versions and random tests
    * ssh-key: the path to the generated SSH-key-file
    * setup: set this to True if an instance is used for the first time and needs configuration.
    * CL-params: a dictionary containing the command line parameters which should be passed to hopper:
        * -f: the path to hopper's xml-configuration file.
        * -o: the path to the final output-file in csv-format.
        * -t: the test type to execute. Available options: "benchmark" or "unit".
        * -b: the version type to use. Available options: "commits", for git commits, and "versions", for Maven versions.
        * --cloud: a tuple containing the bucket-name and the path to the service-account-credentials file (in any order)
    * optional flags:
        * --tests: a list of selected tests to mine, for benchmarks of form '.*\\.BenchA$|.*\\.BenchB$|.*\\.BenchC$', unit tests: 'TestA, TestB, TestC')
        * --step: if specified, only executes every nth versions, defaults to 1.
        * --build-type: defines if builds between versions should be clean or incremental. Available options: "clean" and "inc", defaults to "clean".
        * --skip-noncode: if present, skips versions that do not have a code change (e.g. change only in comment).
# Execution
* Prepare the json-config as stated above.
* Open a new terminal and navigate into ~/clopper/src.
* Execute clopper:


        $ python clopper.py /path/to/json-config.json
        

# Sample json-config script:    
```json
{
  "total":3,
  "ip-list": {
    "instance-1": "12.345.567",
    "instance-2": "12.345.678",
    "instance-3": "12.345.789"
  },
  "project": "/path/to/project-directory",
  "username":"cloudmanager",
  "distribution": "VersionDistributor",
  "ssh-key":"/path/to/ssh-key-file",
  "setup":"True",
  "CL-params": {
    "-f": "/path/to/config.xml",
    "-o": "/path/to/store/final-output.csv",
    "-t": "benchmark",
    "-b": "commits",
    "--tests": "'.*\\.BenchA$|.*\\.BenchB$'",
    "--cloud": "/path/to/storage-credentials.json bucket-name"
    }
}
```

# Important notes
* As the IP-addresses of the instances frequently change, consider running "$ ssh-keygen -f ~/.ssh/known_hosts" before each execution.
* Installation on the instances should take around five minutes. Amongst others, you can monitor its progress in the generated log-file "clopper-log.log". The file will be generated in the /clopper root directory.
* The results should be continuously written to the cloud-storage bucket "clopper-storage" version by version. Besides the generated log-file, you can monitor the program progress in the [console](https://console.cloud.google.com/storage). 

# Troubleshooting
* Man in the middle attack: The IP-address of the concerned instance has most likely been assigned to another instance before. If this is possible, consider running "$ ssh-keygen -f ~/.ssh/known_hosts".
* {..."os_error":"Address already in use","syscall":"bind"}: Run "$ fuser -k X/tcp" on the localhost, X being the port in use and restart the program and "$ ssh -i /path/to/api-key USER@IP fuser -k 8080/tcp" or use the script "recover.py" envoking it with the generated json-config. Then, restart the program.
* Running CTRL Z to quit the execution of clopper only terminates the script on the local host. To force quit on the instances run "$ ssh -i /path/to/api-key USER@IP fuser -k 8080/tcp". This will terminate the grpc-server and thus hopper-execution on the instances. Additionally run "$ fuser -k 222X/tcp" on the local host, X being the instance-name-number of the instance (see above ip-list).
If you plan to restart the program you must run these command as otherwise you will get a "RuntimeError: threads can only be started once". You can also use the script "recover.py" to do so.
