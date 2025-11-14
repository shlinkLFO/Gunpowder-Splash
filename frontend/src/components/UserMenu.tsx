import { Box, Button, Stack, Text } from '@chakra-ui/react'
import { useState } from 'react'
import config from '../config'

export default function UserMenu() {
  const [showLogin, setShowLogin] = useState(false)

  const handleLogin = (provider: 'google' | 'github') => {
    const apiUrl = config.apiBaseUrl || '/api'
    window.location.href = `${apiUrl}/v1/auth/login/${provider}`
  }

  const handleGuestMode = () => {
    localStorage.setItem('guest_mode', 'true')
    window.location.reload()
  }

  return (
    <Box position="relative">
      <Button
        onClick={() => setShowLogin(!showLogin)}
        size="sm"
        colorScheme="blue"
      >
        Log In
      </Button>

      {showLogin && (
        <Box
          position="absolute"
          right={0}
          top="calc(100% + 8px)"
          bg="gray.800"
          borderRadius="md"
          borderWidth="1px"
          borderColor="gray.700"
          p={4}
          minW="250px"
          zIndex={1000}
        >
          <Stack gap={2}>
            <Button
              onClick={() => handleLogin('google')}
              width="100%"
              colorScheme="red"
              size="sm"
            >
              🔴 Login with Google
            </Button>
            <Button
              onClick={() => handleLogin('github')}
              width="100%"
              colorScheme="gray"
              size="sm"
            >
              ⚫ Login with GitHub
            </Button>
            <Button
              onClick={handleGuestMode}
              width="100%"
              variant="outline"
              size="sm"
            >
              Continue as Guest
            </Button>
          </Stack>
        </Box>
      )}
    </Box>
  )
}
