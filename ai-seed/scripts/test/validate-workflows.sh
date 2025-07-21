#!/bin/bash
# Test script for periodic workflow validation
# Path: workflow-testing → validation → reporting

set -euo pipefail

echo "🧪 Testing Periodic Growth Workflows"
echo "==================================="

# Path: workflow-file-validation
echo "📋 Validating workflow files..."

workflow_dir=".github/workflows"
required_workflows=(
    "daily-evolution.yml"
    "weekly-health-check.yml"
    "monthly-evolution-report.yml"
    "quarterly-major-evolution.yml"
)

validation_errors=0

for workflow in "${required_workflows[@]}"; do
    workflow_file="${workflow_dir}/${workflow}"
    
    if [ ! -f "$workflow_file" ]; then
        echo "❌ Missing workflow: $workflow"
        ((validation_errors++))
    else
        echo "✅ Found workflow: $workflow"
        
        # Validate YAML syntax
        if command -v python3 >/dev/null 2>&1; then
            if ! python3 -c "import yaml; yaml.safe_load(open('$workflow_file'))" 2>/dev/null; then
                echo "❌ Invalid YAML syntax in: $workflow"
                ((validation_errors++))
            else
                echo "  ✅ Valid YAML syntax"
            fi
        fi
        
        # Check for required elements
        required_elements=(
            "name:"
            "on:"
            "env:"
            "permissions:"
            "jobs:"
        )
        
        for element in "${required_elements[@]}"; do
            if ! grep -q "$element" "$workflow_file"; then
                echo "  ⚠️ Missing element: $element"
            fi
        done
        
        # Check for evolution version
        if grep -q "EVOLUTION_VERSION.*0.3.0" "$workflow_file"; then
            echo "  ✅ Correct evolution version"
        else
            echo "  ⚠️ Evolution version may be outdated"
        fi
    fi
done

# Path: schedule-validation
echo ""
echo "📅 Validating workflow schedules..."

schedules=(
    "daily-evolution.yml:0 3 \* \* \*"
    "weekly-health-check.yml:0 6 \* \* 0"
    "monthly-evolution-report.yml:0 9 1 \* \*"
    "quarterly-major-evolution.yml:0 12 1 1,4,7,10 \*"
)

for schedule_check in "${schedules[@]}"; do
    workflow_file="${schedule_check%:*}"
    expected_schedule="${schedule_check#*:}"
    
    if [ -f "${workflow_dir}/${workflow_file}" ]; then
        if grep -q "cron.*${expected_schedule}" "${workflow_dir}/${workflow_file}"; then
            echo "✅ Correct schedule for ${workflow_file}"
        else
            echo "⚠️ Schedule may be incorrect for ${workflow_file}"
        fi
    fi
done

# Path: input-validation
echo ""
echo "🎛️ Validating workflow inputs..."

workflows_with_inputs=(
    "daily-evolution.yml"
    "weekly-health-check.yml"
    "monthly-evolution-report.yml"
    "quarterly-major-evolution.yml"
)

for workflow in "${workflows_with_inputs[@]}"; do
    workflow_file="${workflow_dir}/${workflow}"
    
    if [ -f "$workflow_file" ]; then
        if grep -q "workflow_dispatch:" "$workflow_file"; then
            echo "✅ Manual trigger enabled for $workflow"
            
            if grep -q "inputs:" "$workflow_file"; then
                echo "  ✅ Input parameters defined"
            else
                echo "  ⚠️ No input parameters defined"
            fi
        else
            echo "⚠️ No manual trigger for $workflow"
        fi
    fi
done

# Path: output-validation
echo ""
echo "📊 Checking workflow output capabilities..."

output_features=(
    "artifacts"
    "reports"
    "commits"
    "releases"
)

for workflow in "${required_workflows[@]}"; do
    workflow_file="${workflow_dir}/${workflow}"
    
    if [ -f "$workflow_file" ]; then
        echo "Checking outputs for $workflow:"
        
        for feature in "${output_features[@]}"; do
            case "$feature" in
                "artifacts")
                    if grep -q "upload-artifact" "$workflow_file"; then
                        echo "  ✅ Artifact upload"
                    else
                        echo "  ⚠️ No artifact upload"
                    fi
                    ;;
                "reports")
                    if grep -q "report" "$workflow_file"; then
                        echo "  ✅ Report generation"
                    else
                        echo "  ⚠️ No report generation"
                    fi
                    ;;
                "commits")
                    if grep -q "git commit" "$workflow_file"; then
                        echo "  ✅ Automated commits"
                    else
                        echo "  ⚠️ No automated commits"
                    fi
                    ;;
                "releases")
                    if grep -q "release\|tag" "$workflow_file"; then
                        echo "  ✅ Release management"
                    else
                        echo "  ⚠️ No release management"
                    fi
                    ;;
            esac
        done
    fi
done

# Path: results-summary
echo ""
echo "📋 Validation Summary"
echo "===================="

if [ $validation_errors -eq 0 ]; then
    echo "✅ All workflow validations passed!"
    echo ""
    echo "🌱 Periodic Growth Workflows are ready to water your AI-Seed!"
    echo ""
    echo "Workflow Schedule Summary:"
    echo "- Daily Evolution: Every day at 3 AM UTC"
    echo "- Weekly Health Check: Sundays at 6 AM UTC"  
    echo "- Monthly Evolution Report: 1st of each month at 9 AM UTC"
    echo "- Quarterly Major Evolution: Quarterly on 1st at 12 PM UTC"
    echo ""
    echo "🚀 Your seed will now grow automatically through these natural cycles!"
    exit 0
else
    echo "❌ Found $validation_errors validation errors"
    echo "Please fix the issues before deploying workflows"
    exit 1
fi