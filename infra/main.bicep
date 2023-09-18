targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string

@secure()
@description('DBServer administrator password')
param dbserverPassword string

@secure()
@description('Secret Key')
param secretKey string

@description('Id of the user or app to assign application roles')
param principalId string = ''

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var prefix = '${name}-${resourceToken}'
var tags = { 'azd-env-name': name }

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
  location: location
  tags: tags
}

// Store secrets in a keyvault
module keyVault './core/security/keyvault.bicep' = {
  name: 'keyvault'
  scope: resourceGroup
  params: {
    name: '${take(replace(prefix, '-', ''), 17)}-vault'
    location: location
    tags: tags
    principalId: principalId
  }
}

module db 'db.bicep' = {
  name: 'db'
  scope: resourceGroup
  params: {
    name: 'dbserver'
    location: location
    tags: tags
    prefix: prefix
    dbserverDatabaseName: 'relecloud'
    dbserverPassword: dbserverPassword
  }
}

// Monitor application with Azure Monitor
module monitoring 'core/monitor/monitoring.bicep' = {
  name: 'monitoring'
  scope: resourceGroup
  params: {
    location: location
    tags: tags
    applicationInsightsDashboardName: '${prefix}-appinsights-dashboard'
    applicationInsightsName: '${prefix}-appinsights'
    logAnalyticsName: '${prefix}-loganalytics'
  }
}

// Web frontend
module web 'web.bicep' = {
  name: 'web'
  scope: resourceGroup
  params: {
    name: replace('${take(prefix, 19)}-appsvc', '--', '-')
    location: location
    tags: tags
    applicationInsightsName: monitoring.outputs.applicationInsightsName
    keyVaultName: keyVault.outputs.name
    appCommandLine: 'entrypoint.sh'
    pythonVersion: '3.11'
    dbserverDomainName: db.outputs.dbserverDomainName
    dbserverUser: db.outputs.dbserverUser
    dbserverDatabaseName: db.outputs.dbserverDatabaseName
  }
}

var secrets = [
  {
    name: 'DBSERVERPASSWORD'
    value: dbserverPassword
  }
  {
    name: 'SECRETKEY'
    value: secretKey
  }
]

@batchSize(1)
module keyVaultSecrets './core/security/keyvault-secret.bicep' = [for secret in secrets: {
  name: 'keyvault-secret-${secret.name}'
  scope: resourceGroup
  params: {
    keyVaultName: keyVault.outputs.name
    name: secret.name
    secretValue: secret.value
  }
}]

output AZURE_LOCATION string = location
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.endpoint
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
output APPLICATIONINSIGHTS_NAME string = monitoring.outputs.applicationInsightsName