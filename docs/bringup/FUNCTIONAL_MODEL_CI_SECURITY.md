# Functional-model CI security boundary

The execution-backed PTO functional-model gate runs only from
`.github/workflows/functional-model.yml`. That workflow has the stable workflow
name `PTO Functional Model Trusted Push` and the required check identity
`PTO functional-model execution (trusted push)`.

Repository rulesets protecting the integration branch MUST require that exact
push-only check identity. The ordinary `CI / guard` result is not a substitute
for the execution-backed functional-model check.

The trusted workflow is triggered only by a branch push in the base
repository. It checks out `${{ github.sha }}` and executes that pushed tree on
the persistent self-hosted runner. It has no `pull_request`,
`pull_request_target`, or `workflow_dispatch` trigger.

Pull-request workflows run only GitHub-hosted/static jobs. A fork pull request
cannot trigger the base repository's push-only required check and therefore
remains unsatisfied. To obtain the check, a maintainer must mirror the exact
fork head commit to a trusted branch in the base repository, or use a
separately authorized ephemeral runner lane. Labels and secrets are not runner
authorization mechanisms.
