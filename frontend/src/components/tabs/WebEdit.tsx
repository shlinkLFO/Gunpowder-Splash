import { useState } from 'react'
import { Box, Grid, GridItem, Text, Button, HStack } from '@chakra-ui/react'
import Editor from '@monaco-editor/react'

function WebEdit() {
  const [html, setHtml] = useState(`<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Preview</title>
</head>
<body>
    <h1>Hello World!</h1>
    <p>Edit HTML, CSS, and JavaScript to see live updates.</p>
</body>
</html>`)

  const [css, setCss] = useState(`body {
    font-family: Arial, sans-serif;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

h1 {
    text-align: center;
}`)

  const [js, setJs] = useState(`console.log('JavaScript is ready!');

// Add your JavaScript code here
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded!');
});`)

  const [previewKey, setPreviewKey] = useState(0)

  const getPreviewContent = () => {
    return `
      <!DOCTYPE html>
      <html>
        <head>
          <style>${css}</style>
        </head>
        <body>
          ${html}
          <script>${js}</script>
        </body>
      </html>
    `
  }

  const refreshPreview = () => {
    setPreviewKey(prev => prev + 1)
  }

  return (
    <Box h="100%">
      <HStack mb={4} justify="space-between">
        <Text fontSize="lg" color="midnight.400" fontWeight="bold">
          Web Editor - HTML, CSS, JavaScript
        </Text>
        <Button size="sm" onClick={refreshPreview}>
          🔄 Refresh Preview
        </Button>
      </HStack>

      <Grid 
        templateRows="1fr 1fr" 
        templateColumns="1fr 1fr" 
        gap={4} 
        h="calc(100% - 60px)"
      >
        <GridItem>
          <Box h="100%" border="1px solid" borderColor="midnight.700" borderRadius="md" overflow="hidden">
            <Box bg="midnight.800" px={3} py={2}>
              <Text fontSize="sm" color="midnight.400" fontWeight="bold">HTML</Text>
            </Box>
            <Editor
              height="calc(100% - 40px)"
              language="html"
              value={html}
              onChange={(value) => setHtml(value || '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 13,
                lineNumbers: 'on',
                automaticLayout: true,
              }}
            />
          </Box>
        </GridItem>

        <GridItem>
          <Box h="100%" border="1px solid" borderColor="midnight.700" borderRadius="md" overflow="hidden">
            <Box bg="midnight.800" px={3} py={2}>
              <Text fontSize="sm" color="midnight.400" fontWeight="bold">CSS</Text>
            </Box>
            <Editor
              height="calc(100% - 40px)"
              language="css"
              value={css}
              onChange={(value) => setCss(value || '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 13,
                lineNumbers: 'on',
                automaticLayout: true,
              }}
            />
          </Box>
        </GridItem>

        <GridItem>
          <Box h="100%" border="1px solid" borderColor="midnight.700" borderRadius="md" overflow="hidden">
            <Box bg="midnight.800" px={3} py={2}>
              <Text fontSize="sm" color="midnight.400" fontWeight="bold">JavaScript</Text>
            </Box>
            <Editor
              height="calc(100% - 40px)"
              language="javascript"
              value={js}
              onChange={(value) => setJs(value || '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 13,
                lineNumbers: 'on',
                automaticLayout: true,
              }}
            />
          </Box>
        </GridItem>

        <GridItem>
          <Box h="100%" border="1px solid" borderColor="midnight.700" borderRadius="md" overflow="hidden">
            <Box bg="midnight.800" px={3} py={2}>
              <Text fontSize="sm" color="midnight.400" fontWeight="bold">Live Preview</Text>
            </Box>
            <Box h="calc(100% - 40px)" bg="white">
              <iframe
                key={previewKey}
                srcDoc={getPreviewContent()}
                style={{
                  width: '100%',
                  height: '100%',
                  border: 'none',
                }}
                title="preview"
                sandbox="allow-scripts"
              />
            </Box>
          </Box>
        </GridItem>
      </Grid>
    </Box>
  )
}

export default WebEdit
