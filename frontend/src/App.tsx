import { Box, Flex, Text, Alert } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import MainContent from './components/MainContent'
import LandingPage from './pages/LandingPage'
import UserMenu from './components/UserMenu'

function App() {
  const [selectedFile, setSelectedFile] = useState<string | undefined>()
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    // Check for auth token or guest mode
    const token = localStorage.getItem('auth_token')
    const guestMode = localStorage.getItem('guest_mode')
    
    if (token || guestMode === 'true') {
      setIsAuthenticated(true)
    } else {
      setIsAuthenticated(false)
    }

    // Check for OAuth callback with token or error in URL
    const urlParams = new URLSearchParams(window.location.search)
    const tokenFromUrl = urlParams.get('token')
    const refreshTokenFromUrl = urlParams.get('refresh_token')
    const errorFromUrl = urlParams.get('error')
    
    if (tokenFromUrl) {
      localStorage.setItem('auth_token', tokenFromUrl)
      if (refreshTokenFromUrl) {
        localStorage.setItem('refresh_token', refreshTokenFromUrl)
      }
      localStorage.removeItem('guest_mode') // Clear guest mode if logging in
      setIsAuthenticated(true)
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname)
    } else if (errorFromUrl) {
      // Show error message
      setErrorMessage(errorFromUrl)
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname)
      // Auto-hide error after 10 seconds
      setTimeout(() => setErrorMessage(null), 10000)
    }
  }, [])

  const handleContinueAsGuest = () => {
    localStorage.setItem('guest_mode', 'true')
    setIsAuthenticated(true)
  }

  // Loading state
  if (isAuthenticated === null) {
    return (
      <Flex h="100vh" bg="gray.900" alignItems="center" justifyContent="center">
        <Box color="gray.400">Loading...</Box>
      </Flex>
    )
  }

  // Show landing page if not authenticated
  if (!isAuthenticated) {
    return <LandingPage onContinueAsGuest={handleContinueAsGuest} />
  }

  // Show main IDE
  return (
    <Flex h="100vh" bg="gray.900" flexDirection="column">
      {/* Error Alert */}
      {errorMessage && (
        <Alert.Root status="error" position="absolute" top={4} left="50%" transform="translateX(-50%)" maxW="600px" zIndex={9999}>
          <Alert.Indicator />
          <Box flex="1">
            <Alert.Title>Account Linking Failed</Alert.Title>
            <Alert.Description>{errorMessage}</Alert.Description>
          </Box>
          <Box
            as="button"
            onClick={() => setErrorMessage(null)}
            ml={2}
            color="red.700"
            fontWeight="bold"
            cursor="pointer"
            _hover={{ opacity: 0.8 }}
          >
            ✕
          </Box>
        </Alert.Root>
      )}

      {/* Top Header Bar */}
      <Flex
        h="50px"
        bg="gray.800"
        borderBottom="1px solid"
        borderColor="gray.700"
        px={4}
        alignItems="center"
        justifyContent="space-between"
      >
        <Text color="white" fontWeight="bold">Gunpowder Splash</Text>
        <UserMenu />
      </Flex>

      {/* Main Content Area - Temporarily simplified */}
      <Flex flex="1" overflow="hidden">
        <Sidebar onFileSelect={setSelectedFile} selectedFile={selectedFile} />
        <Box flex="1" overflow="hidden">
          <MainContent selectedFile={selectedFile} />
        </Box>
      </Flex>
    </Flex>
  )
}

export default App
