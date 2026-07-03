import * as cdk from "aws-cdk-lib";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as iam from "aws-cdk-lib/aws-iam";
import { Construct } from "constructs";

/**
 * Provisions all AWS resources for Mosaic:
 * - 3x DynamoDB tables (users, personas, transactions), PAY_PER_REQUEST
 * - 1x versioned private S3 bucket for model artifacts
 * - 4x Lambda functions (plaid-sync, classify-user, generate-persona, get-persona)
 * - 1x API Gateway REST API with CORS
 * - Least-privilege IAM roles per Lambda
 *
 * TODO: flesh out Lambda code assets under backend/lambdas, wire routes,
 * and scope IAM policies down to the specific table/bucket/model ARNs.
 */
export class MosaicStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const usersTable = new dynamodb.Table(this, "UsersTable", {
      tableName: "mosaic-users",
      partitionKey: { name: "userId", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
    });

    const personasTable = new dynamodb.Table(this, "PersonasTable", {
      tableName: "mosaic-personas",
      partitionKey: { name: "personaId", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
    });

    const transactionsTable = new dynamodb.Table(this, "TransactionsTable", {
      tableName: "mosaic-transactions",
      partitionKey: { name: "userId", type: dynamodb.AttributeType.STRING },
      sortKey: { name: "transactionId", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
    });

    // Bucket name is auto-generated (CDK appends account/region/hash) since
    // S3 bucket names are globally unique across all AWS accounts, not just
    // this one — a fixed name like "mosaic-models" collides with any other
    // AWS customer who already claimed it.
    const modelBucket = new s3.Bucket(this, "ModelBucket", {
      versioned: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    const api = new apigateway.RestApi(this, "MosaicApi", {
      restApiName: "mosaic-api",
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      },
    });

    // TODO: create Lambda functions from backend/lambdas/*.py, grant each
    // least-privilege access to only the tables/bucket/model it needs, and
    // wire them to api.root routes (/sync/{userId}, /classify/{userId},
    // /persona/generate/{clusterId}, /persona/{userId}).

    new cdk.CfnOutput(this, "ApiUrl", { value: api.url });
    new cdk.CfnOutput(this, "ModelBucketName", { value: modelBucket.bucketName });
  }
}
