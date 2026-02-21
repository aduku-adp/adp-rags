# adp-rags
The repository of the Aduku Platform (ADP) RAG applications


https://201714515140.signin.aws.amazon.com/console


### Setup authentication - create access key

To create the cluster we will use `adp-app-admin` user.
Get or create an access key for the user.

Example:

```
adp-app-admin
Access key:************
Secret access key:****************
```

### Configure AWS CLI

- Install AWS CLI

```
sudo softwareupdate --install-rosetta
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
pip3 install awscli --upgrade --user
```

- Configure aws cli using adp-app-admin credentials

```
$ aws configure --profile adp-app-admin
AWS Access Key ID [None]: <**************>
AWS Secret Access Key [None]: <************>
Default region name [None]: eu-central-1
Default output format [None]: json
```
