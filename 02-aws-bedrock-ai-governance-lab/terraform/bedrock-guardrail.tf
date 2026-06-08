resource "aws_bedrock_guardrail" "ai_governance" {
  name                      = var.project_name
  description               = "Governance guardrail for a sandbox AWS Bedrock AI application."
  blocked_input_messaging   = "This request was blocked by the AI governance policy. Please rephrase the request."
  blocked_outputs_messaging = "The generated response was blocked by the AI governance policy."

  content_policy_config {
    filters_config {
      type            = "HATE"
      input_strength  = "MEDIUM"
      output_strength = "MEDIUM"
    }
    filters_config {
      type            = "INSULTS"
      input_strength  = "MEDIUM"
      output_strength = "MEDIUM"
    }
    filters_config {
      type            = "MISCONDUCT"
      input_strength  = "HIGH"
      output_strength = "HIGH"
    }
    filters_config {
      type            = "PROMPT_ATTACK"
      input_strength  = "HIGH"
      output_strength = "NONE"
    }
    filters_config {
      type            = "VIOLENCE"
      input_strength  = "MEDIUM"
      output_strength = "MEDIUM"
    }
  }

  sensitive_information_policy_config {
    pii_entities_config {
      type   = "EMAIL"
      action = "ANONYMIZE"
    }
    pii_entities_config {
      type   = "PHONE"
      action = "ANONYMIZE"
    }
    pii_entities_config {
      type   = "US_SOCIAL_SECURITY_NUMBER"
      action = "BLOCK"
    }
  }

  topic_policy_config {
    topics_config {
      name       = "Restricted professional advice"
      type       = "DENY"
      definition = "Requests for guaranteed legal, medical, or financial advice that should be handled by qualified professionals."
      examples = [
        "Give me guaranteed legal advice for my court case.",
        "Tell me exactly how to avoid all taxes.",
        "Prescribe medicine for my symptoms."
      ]
    }
  }

  tags = local.common_tags
}

resource "aws_bedrock_guardrail_version" "ai_governance" {
  guardrail_arn = aws_bedrock_guardrail.ai_governance.guardrail_arn
  description   = "Initial published version for the AI governance lab."
}
