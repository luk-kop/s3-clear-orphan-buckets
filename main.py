import boto3


def get_active_stacks_ids() -> list:
    """
    Return the list of current running CloudFormation stacks ids.
    """
    client = boto3.client('cloudformation')
    response = client.list_stacks(
        StackStatusFilter=[
            'CREATE_IN_PROGRESS',
            'CREATE_COMPLETE'
        ]
    )
    stack_ids = [stack['StackId'] for stack in response['StackSummaries']]
    return stack_ids


def check_stack_status(stack_id: str, active_stacks_ids: list) -> bool:
    return stack_id in active_stacks_ids




if __name__ == '__main__':
    print(get_active_stacks_ids())
