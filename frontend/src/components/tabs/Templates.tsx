import { useState, useEffect } from 'react'
import { Box, Grid, Text, Button, VStack, HStack } from '@chakra-ui/react'
import Editor from '@monaco-editor/react'

interface Template {
  id: string
  name: string
  description: string
  language: string
  code: string
}

const TEMPLATES: Template[] = [
  {
    id: 'python_basic',
    name: 'Python - Basic Script',
    description: 'Basic Python script template with common imports',
    language: 'python',
    code: `import pandas as pd
import numpy as np

# Your code here
print("Hello from Python!")

# Example: Create a DataFrame
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6]
})
print(df)
`
  },
  {
    id: 'python_data_analysis',
    name: 'Python - Data Analysis',
    description: 'Data analysis template with pandas and visualization',
    language: 'python',
    code: `import pandas as pd
import numpy as np
import plotly.express as px

# Load data
# df = pd.read_csv('data.csv')

# Create sample data
df = pd.DataFrame({
    'category': ['A', 'B', 'C', 'D'],
    'values': np.random.randint(10, 100, 4)
})

# Data analysis
print("Dataset Info:")
print(df.describe())

# Visualization
fig = px.bar(df, x='category', y='values', title='Sample Bar Chart')
fig.show()
`
  },
  {
    id: 'python_ml',
    name: 'Python - Machine Learning',
    description: 'Basic ML template setup',
    language: 'python',
    code: `import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Create sample data
X = np.random.rand(100, 5)
y = np.random.rand(100)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"Model R² Score: {score:.4f}")
`
  },
  {
    id: 'javascript_basic',
    name: 'JavaScript - Basic',
    description: 'Basic JavaScript template',
    language: 'javascript',
    code: `// Basic JavaScript template
console.log('Hello from JavaScript!');

// Function example
function greet(name) {
    return \`Hello, \${name}!\`;
}

console.log(greet('World'));

// Array operations
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
console.log('Doubled:', doubled);
`
  },
  {
    id: 'html_starter',
    name: 'HTML - Starter Page',
    description: 'HTML5 starter template',
    language: 'html',
    code: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Web Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>Welcome!</h1>
    <p>This is your starter page.</p>
</body>
</html>
`
  }
]

interface TemplatesProps {
  onLoadTemplate?: (code: string) => void
}

function Templates({ onLoadTemplate }: TemplatesProps) {
  const [selectedTemplate, setSelectedTemplate] = useState<Template>(TEMPLATES[0])
  const [code, setCode] = useState(TEMPLATES[0].code)

  useEffect(() => {
    setCode(selectedTemplate.code)
  }, [selectedTemplate])

  const handleLoad = () => {
    if (onLoadTemplate) {
      onLoadTemplate(code)
      alert('Template loaded! Switch to Code Editor tab to use it.')
    }
  }

  return (
    <Box h="100%">
      <Text fontSize="lg" color="midnight.400" fontWeight="bold" mb={4}>
        Code Templates
      </Text>

      <Grid templateColumns="300px 1fr" gap={4} h="calc(100% - 60px)">
        <VStack align="stretch" gap={2} overflowY="auto">
          {TEMPLATES.map((template) => (
            <Box
              key={template.id}
              p={3}
              border="1px solid"
              borderColor={selectedTemplate.id === template.id ? 'purple.500' : 'midnight.700'}
              borderRadius="md"
              cursor="pointer"
              bg={selectedTemplate.id === template.id ? 'rgba(128, 90, 213, 0.1)' : 'transparent'}
              _hover={{ borderColor: 'purple.400' }}
              onClick={() => setSelectedTemplate(template)}
            >
              <Text fontSize="sm" fontWeight="bold" color="midnight.400">
                {template.name}
              </Text>
              <Text fontSize="xs" color="midnight.500" mt={1}>
                {template.description}
              </Text>
            </Box>
          ))}
        </VStack>

        <VStack align="stretch" gap={3} h="100%">
          <HStack justify="space-between">
            <Text fontSize="md" color="midnight.400" fontWeight="bold">
              {selectedTemplate.name}
            </Text>
            <Button size="sm" colorScheme="purple" onClick={handleLoad}>
              📝 Use Template
            </Button>
          </HStack>

          <Box 
            flex="1" 
            border="1px solid" 
            borderColor="midnight.700" 
            borderRadius="md"
            overflow="hidden"
          >
            <Editor
              height="100%"
              language={selectedTemplate.language}
              value={code}
              onChange={(value) => setCode(value || '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                readOnly: false,
                automaticLayout: true,
              }}
            />
          </Box>
        </VStack>
      </Grid>
    </Box>
  )
}

export default Templates
