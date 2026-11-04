# Policy-as-Code: deployment rules every Kubernetes manifest must pass.
# Evaluated in CI with Conftest; a single violation fails the pipeline.
package main

import rego.v1

containers contains c if {
	input.kind == "Deployment"
	some c in input.spec.template.spec.containers
}

deny contains msg if {
	input.kind == "Deployment"
	not input.spec.template.spec.securityContext.runAsNonRoot
	msg := sprintf("%s: pod must set securityContext.runAsNonRoot=true", [input.metadata.name])
}

deny contains msg if {
	some c in containers
	not c.securityContext.readOnlyRootFilesystem
	msg := sprintf("container '%s' must use readOnlyRootFilesystem", [c.name])
}

deny contains msg if {
	some c in containers
	c.securityContext.allowPrivilegeEscalation != false
	msg := sprintf("container '%s' must set allowPrivilegeEscalation=false", [c.name])
}

deny contains msg if {
	some c in containers
	c.securityContext.privileged == true
	msg := sprintf("container '%s' must not be privileged", [c.name])
}

deny contains msg if {
	some c in containers
	not "ALL" in c.securityContext.capabilities.drop
	msg := sprintf("container '%s' must drop ALL capabilities", [c.name])
}

deny contains msg if {
	some c in containers
	not c.resources.limits.memory
	msg := sprintf("container '%s' must define a memory limit", [c.name])
}

deny contains msg if {
	some c in containers
	endswith(c.image, ":latest")
	msg := sprintf("container '%s' uses ':latest'; pin a version or commit SHA", [c.name])
}
