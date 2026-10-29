#!/usr/bin/env node
// API Structure Test - Validates backend architecture
// Path: Structure Validation → Component Check → Readiness Report

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Path: API structure validation
const validateAPIStructure = () => {
    const requiredFiles = [
        'src/index.js',
        'src/routes/health.js',
        'src/routes/metrics.js',
        'src/routes/paths.js',
        'src/routes/evolution.js',
        'package.json'
    ];

    const missingFiles = [];
    let validationScore = 0;

    for (const file of requiredFiles) {
        const filePath = path.join(__dirname, file);
        if (fs.existsSync(filePath)) {
            validationScore++;
        } else {
            missingFiles.push(file);
        }
    }

    return {
        score: validationScore,
        total: requiredFiles.length,
        missing: missingFiles,
        isReady: missingFiles.length === 0
    };
};

// Path: Package dependencies validation
const validateDependencies = () => {
    const packagePath = path.join(__dirname, 'package.json');
    
    if (!fs.existsSync(packagePath)) {
        return { isValid: false, reason: 'package.json not found' };
    }

    try {
        const packageData = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
        const requiredDeps = ['express', 'cors', 'helmet', 'morgan'];
        const missingDeps = requiredDeps.filter(dep => !packageData.dependencies?.[dep]);
        
        return {
            isValid: missingDeps.length === 0,
            missing: missingDeps,
            hasDevDeps: !!packageData.devDependencies,
            hasScripts: !!packageData.scripts
        };
    } catch (error) {
        return { isValid: false, reason: 'Invalid package.json format' };
    }
};

// Path: Main validation execution
const main = () => {
    console.log('🔗 AI-Seed API Structure Validation');
    console.log('=====================================');

    // Validate file structure
    const structureResult = validateAPIStructure();
    console.log(`📁 File Structure: ${structureResult.score}/${structureResult.total} files present`);
    
    if (structureResult.missing.length > 0) {
        console.log(`❌ Missing files: ${structureResult.missing.join(', ')}`);
    } else {
        console.log('✅ All required files present');
    }

    // Validate dependencies
    const depsResult = validateDependencies();
    if (depsResult.isValid) {
        console.log('✅ Dependencies correctly configured');
        console.log(`✅ Development dependencies: ${depsResult.hasDevDeps ? 'Present' : 'Missing'}`);
        console.log(`✅ NPM scripts: ${depsResult.hasScripts ? 'Configured' : 'Missing'}`);
    } else {
        console.log(`❌ Dependencies issue: ${depsResult.reason || 'Missing deps: ' + depsResult.missing?.join(', ')}`);
    }

    // Final readiness check
    const isReady = structureResult.isReady && depsResult.isValid;
    console.log('');
    console.log(`🚀 API Readiness: ${isReady ? 'READY' : 'NOT READY'}`);
    
    if (isReady) {
        console.log('✨ API structure validated and ready for container deployment!');
        console.log('API structure validation ready');
    } else {
        console.log('⚠️  Some components need attention before deployment');
        process.exit(1);
    }
};

// Execute if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}

export { validateAPIStructure, validateDependencies };