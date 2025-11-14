import { Box, Flex, Text, Button, Stack } from '@chakra-ui/react'
import config from '../config'

interface LoginPageProps {
  onBack: () => void
}

export default function LoginPage({ onBack }: LoginPageProps) {
  const handleLogin = (provider: 'google' | 'github') => {
    const apiUrl = config.apiBaseUrl || '/api'
    window.location.href = `${apiUrl}/v1/auth/login/${provider}`
  }

  return (
    <Flex h="100vh" bg="gray.900" alignItems="center" justifyContent="center">
      <Box maxW="500px" w="100%" p={8}>
        {/* Logo/Title */}
        <Box textAlign="center" mb={12}>
          <Text
            fontSize="6xl"
            fontWeight="bold"
            bgGradient="linear(to-r, red.400, orange.400)"
            bgClip="text"
            mb={4}
          >
            Gunpowder Splash
          </Text>
          <Text color="gray.400" fontSize="xl">
            Sign in to your account
          </Text>
        </Box>

        {/* Login Options */}
        <Stack gap={4}>
          <Button
            onClick={() => handleLogin('google')}
            size="lg"
            colorScheme="red"
            width="100%"
            height="60px"
            fontSize="lg"
          >
            Login with Google
          </Button>
          
          <Button
            onClick={() => handleLogin('github')}
            size="lg"
            colorScheme="gray"
            width="100%"
            height="60px"
            fontSize="lg"
          >
            Login with GitHub
          </Button>

          <Button
            onClick={onBack}
            size="md"
            variant="ghost"
            width="100%"
            mt={4}
            color="gray.400"
            _hover={{ color: 'white', bg: 'gray.800' }}
          >
            Back to App
          </Button>
        </Stack>

        {/* Footer Info */}
        <Box mt={12} textAlign="center">
          <Text color="gray.600" fontSize="sm">
            By signing in, you agree to our Terms of Service
          </Text>
        </Box>
      </Box>
    </Flex>
  )
}

