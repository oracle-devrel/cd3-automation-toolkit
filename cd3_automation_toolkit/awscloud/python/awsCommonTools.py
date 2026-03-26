import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def read_aws_auth_properties(filepath):

    aws_access_key_id = None
    aws_secret_access_key = None

    with open(filepath, "r") as f:

        for line in f:
            line = line.strip()
            if line == "" or line.startswith("#") or line.startswith("["):
                continue

            if line.startswith("aws_access_key_id"):
                aws_access_key_id = line.split("=", 1)[1].strip()

            elif line.startswith("aws_secret_access_key"):
                aws_secret_access_key = line.split("=", 1)[1].strip()


    if not aws_access_key_id or not aws_secret_access_key:
        print("Missing AWS authentication parameters in properties file")
        exit(1)

    return aws_access_key_id, aws_secret_access_key


class awsCommonTools():

    def authenticate(self, propsfile):

        aws_access_key_id, aws_secret_access_key = read_aws_auth_properties(propsfile)

        try:

            session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name="us-east-1"
            )

            # validate credentials
            sts = session.client("sts")
            sts.get_caller_identity()

            return session

        except NoCredentialsError:
            print("AWS credentials not found")
            exit(1)

        except ClientError as e:
            print("Invalid AWS credentials:", e)
            exit(1)