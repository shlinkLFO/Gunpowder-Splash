import { Box, Button, Stack, Avatar, Text, Flex } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import config from '../config'

interface UserInfo {
  id: string
  email: string
  display_name?: string
  avatar_url?: string
  provider: string
}

export default function UserMenu() {
  const [showMenu, setShowMenu] = useState(false)
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null)
  const [isGuest, setIsGuest] = useState(false)

  useEffect(() => {
    // Check if guest mode
    const guestMode = localStorage.getItem('guest_mode')
    if (guestMode === 'true') {
      setIsGuest(true)
      return
    }

    // Fetch user info if authenticated
    const token = localStorage.getItem('auth_token')
    if (token) {
      fetchUserInfo(token)
    }
  }, [])

  const fetchUserInfo = async (token: string) => {
    try {
      const apiUrl = config.apiBaseUrl || '/api'
      const response = await fetch(`${apiUrl}/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUserInfo(data)
      } else if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('auth_token')
        localStorage.removeItem('refresh_token')
        window.location.reload()
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error)
    }
  }

  const handleLogin = (provider: 'google' | 'github') => {
    const apiUrl = config.apiBaseUrl || '/api'
    window.location.href = `${apiUrl}/v1/auth/login/${provider}`
  }

  const handleGuestMode = () => {
    localStorage.setItem('guest_mode', 'true')
    window.location.reload()
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('guest_mode')
    window.location.reload()
  }

  // If authenticated, show user avatar/name
  if (userInfo) {
    return (
      <Box position="relative">
        <Flex
          alignItems="center"
          gap={2}
          cursor="pointer"
          onClick={() => setShowMenu(!showMenu)}
        >
          <Avatar
            size="sm"
            name={userInfo.display_name || userInfo.email}
            src={userInfo.avatar_url}
          />
          <Text color="white" fontSize="sm">
            {userInfo.display_name || userInfo.email.split('@')[0]}
          </Text>
        </Flex>

        {showMenu && (
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
              <Text color="gray.400" fontSize="xs">
                {userInfo.email}
              </Text>
              <Text color="gray.500" fontSize="xs">
                Signed in with {userInfo.provider === 'google' ? 'Google' : 'GitHub'}
              </Text>
              <Button
                onClick={handleLogout}
                width="100%"
                variant="outline"
                size="sm"
                colorScheme="red"
              >
                Log Out
              </Button>
            </Stack>
          </Box>
        )}
      </Box>
    )
  }

  // If guest mode
  if (isGuest) {
    return (
      <Box position="relative">
        <Button
          onClick={() => setShowMenu(!showMenu)}
          size="sm"
          variant="ghost"
          colorScheme="gray"
        >
          Guest Mode
        </Button>

        {showMenu && (
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
              <Text color="gray.400" fontSize="sm">
                You're in guest mode
              </Text>
              <Button
                onClick={() => handleLogin('google')}
                width="100%"
                colorScheme="red"
                size="sm"
              >
                Login with Google
              </Button>
              <Button
                onClick={() => handleLogin('github')}
                width="100%"
                colorScheme="gray"
                size="sm"
              >
                Login with GitHub
              </Button>
            </Stack>
          </Box>
        )}
      </Box>
    )
  }

  // Not authenticated - show login button
  return (
    <Box position="relative">
      <Button
        onClick={() => setShowMenu(!showMenu)}
        size="sm"
        colorScheme="blue"
      >
        Log In
      </Button>

      {showMenu && (
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
              Login with Google
            </Button>
            <Button
              onClick={() => handleLogin('github')}
              width="100%"
              colorScheme="gray"
              size="sm"
            >
              Login with GitHub
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
