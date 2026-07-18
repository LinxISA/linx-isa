## Summary

Describe what this PR changes and why.

## Validation

- [ ] `bash tools/ci/check_repo_layout.sh`
- [ ] `python3 tools/isa/build_golden.py --profile v0.57 --check`
- [ ] `python3 tools/isa/validate_spec.py --profile v0.57`
- [ ] `python3 tools/isa/check_canonical_v057.py --root .`
- [ ] `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml`
- [ ] `python3 tools/bringup/check_sail_model.py`
- [ ] `mkdocs build --strict`
- [ ] (Optional) `python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr`
- [ ] (Optional) `bash tools/regression/run.sh`

## Submodules (if touched)

- [ ] Submodule SHAs are intentional and minimal
- [ ] `.gitmodules` URLs remain in the LinxISA org
- [ ] Any cross-repo change was merged upstream first
