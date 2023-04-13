import openai
import boto3
from botocore.exceptions import ClientError


def get_secret():

    secret_name = "chatgpt"
    region_name = "us-east-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']

    return secret[12:-2]


def gpt3_recipe(recipe_name):
    openai.api_key = get_secret()

    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=f"How do I make the following:\n\n{recipe_name}",
      temperature=0.5,
      max_tokens=1000,
      top_p=1.0,
      frequency_penalty=0.8,
      presence_penalty=0.0
    )

    return list(list(response.values())[4][0].values())[0].replace("\n", "")
