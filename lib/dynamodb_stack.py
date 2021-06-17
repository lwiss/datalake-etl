# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk.core as cdk
import aws_cdk.aws_dynamodb as dynamodb

from .configuration import (
    PROD, TEST, get_logical_id_prefix, get_resource_name_prefix,
)


def get_transformation_rules_table_name(resource_name_prefix: str) -> str:
    return f'{resource_name_prefix}_etl_transformation_rules'

class DynamoDbStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, target_environment: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        logical_id_prefix = get_logical_id_prefix()
        resource_name_prefix = get_resource_name_prefix().replace('-', '_')

        self.removal_policy = cdk.RemovalPolicy.RETAIN if (target_environment == PROD 
            or target_environment == TEST) else cdk.RemovalPolicy.DESTROY

        self.job_audit_table = self.create_table(
            f'{target_environment}{logical_id_prefix}EtlAuditTable',
            f'{target_environment.lower()}-{resource_name_prefix}-etl-job-audit',
            'id',
        )

        transformation_table = get_transformation_rules_table_name(resource_name_prefix)
        self.transformation_rules_table = self.create_table(
            f'{target_environment}{logical_id_prefix}EtlTransformationRulesTable',
            f'{target_environment}_{transformation_table}',
            'load_name',
        )

    def create_table(self, construct_name, table_name, partition_key, sort_key = None) -> dynamodb.Table:
        return dynamodb.Table(self,
            construct_name,
            table_name=table_name,
            partition_key=dynamodb.Attribute(name=partition_key, type=dynamodb.AttributeType.STRING),
            sort_key=sort_key,
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            encryption=dynamodb.TableEncryption.DEFAULT,
            point_in_time_recovery=False,
            read_capacity=5,
            removal_policy=self.removal_policy,
            write_capacity=5,
        )
