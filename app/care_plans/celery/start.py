import core.aws.sfn as sfn


def run(state_machine_arn: str, input_: dict, aws_region: str = "eu-west-3"):
    print(f"START StateMachine [{state_machine_arn}]")

    return sfn.AwsStepFunctions(aws_region).start_execution(state_machine_arn=state_machine_arn,
                                                            input_={"input": input_})
