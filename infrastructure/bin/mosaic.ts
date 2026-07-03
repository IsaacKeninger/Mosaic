#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { MosaicStack } from "../lib/mosaic-stack";

const app = new cdk.App();

new MosaicStack(app, "MosaicStack", {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.AWS_REGION ?? "us-east-1",
  },
});
