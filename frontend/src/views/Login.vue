<template>
	<ion-page>
		<ion-content :fullscreen="true" class="bg-white">
			<div v-if="resetPassword.showDialog" class="flex min-h-screen flex-col bg-white">
				<header class="flex items-center justify-between px-6 py-4">
					<div class="text-lg font-semibold">{{ __("Reset Password") }}</div>
					<button type="button" class="text-sm underline" @click="resetPassword.showDialog = false">
						{{ __("Back to Login") }}
					</button>
				</header>
				<div class="flex flex-1 flex-col items-center justify-center px-8 text-center">
					<p>{{ __("Your password has expired. Please reset your password to continue") }}</p>
					<a class="mt-6 rounded bg-black px-4 py-2 text-white" :href="resetPassword.link" target="_blank">
						{{ __("Go to Reset Password page") }}
					</a>
				</div>
			</div>

			<div v-else class="flex min-h-screen w-full items-center justify-center bg-white px-4 py-10">
				<div class="w-full max-w-md">
					<div class="mb-8 text-center">
						<div class="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-black text-sm font-bold text-white">
							PP
						</div>
						<div class="text-2xl font-semibold">PeoplePay360</div>
						<p class="mt-1 text-sm text-gray-500">{{ __("Choose a role to autofill demo login") }}</p>
					</div>

					<div v-if="!user_pass_login_disabled.data" class="mb-4 grid grid-cols-2 gap-2">
						<button
							v-for="role in roleProfiles"
							:key="role.id"
							type="button"
							class="rounded-lg border px-3 py-2 text-left text-sm"
							:class="selectedRole === role.id ? 'border-black bg-black text-white' : 'border-gray-300 bg-white'"
							@click="selectRole(role)"
						>
							<div class="font-semibold">{{ role.label }}</div>
							<div class="mt-0.5 text-[11px] opacity-75">{{ role.description }}</div>
						</button>
					</div>

					<div v-if="!user_pass_login_disabled.data" class="rounded-lg border border-gray-200 p-5">
						<div v-if="activeRole" class="mb-3 rounded-md bg-gray-50 px-3 py-2 text-xs text-gray-700">
							{{ activeRole.label }} ·
							<span class="font-mono font-semibold text-black">{{ activeRole.password }}</span>
						</div>
						<form class="flex flex-col space-y-3" @submit.prevent="submit">
							<Input :label="__('Email')" v-model="email" type="text" autocomplete="username" />
							<Input
								:label="__('Password')"
								type="password"
								v-model="password"
								autocomplete="current-password"
							/>
							<ErrorMessage :message="errorMessage" />
							<Button :loading="session.login.loading" variant="solid" class="!mt-2">
								{{ __("Continue as") }} {{ activeRole?.label || __("User") }}
							</Button>
						</form>
					</div>
				</div>
			</div>

			<Dialog v-model="otp.showDialog">
				<template #body-title>
					<h2 class="text-lg font-bold">{{ __("OTP Verification") }}</h2>
				</template>
				<template #body-content>
					<form class="flex flex-col space-y-4" @submit.prevent="submit">
						<Input :label="__('OTP Code')" type="text" v-model="otp.code" />
						<ErrorMessage :message="errorMessage" />
						<Button :loading="session.otp.loading" variant="solid">{{ __("Verify") }}</Button>
					</form>
				</template>
			</Dialog>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonPage, IonContent } from "@ionic/vue"
import { computed, inject, reactive, ref } from "vue"
import { Input, Button, ErrorMessage, Dialog, createResource } from "frappe-ui"
import { DEMO_ROLE_LOGINS } from "@/data/demoLogins"

const email = ref("")
const password = ref("")
const errorMessage = ref("")
const selectedRole = ref("employee")
const resetPassword = reactive({ showDialog: false, link: "" })
const otp = reactive({ showDialog: false, tmp_id: "", code: "", verification: {} })
const session = inject("$session")
const __ = inject("$translate")

const remoteRoles = createResource({
	url: "hrms.peoplepay360.roles.get_demo_role_logins",
	auto: true,
	onSuccess(data) {
		if (data?.roles?.length) {
			const match = data.roles.find((r) => r.id === selectedRole.value) || data.roles[0]
			selectRole(match)
		}
	},
})

const roleProfiles = computed(() => remoteRoles.data?.roles || DEMO_ROLE_LOGINS)
const activeRole = computed(() => roleProfiles.value.find((r) => r.id === selectedRole.value))

function selectRole(role) {
	selectedRole.value = role.id
	email.value = role.email
	password.value = role.password
}
selectRole(DEMO_ROLE_LOGINS[0])

async function submit() {
	try {
		let response
		if (otp.showDialog) response = await session.otp(otp.tmp_id, otp.code)
		else response = await session.login(email.value, password.value)

		if (response.message === "Password Reset") {
			resetPassword.showDialog = true
			resetPassword.link = response.redirect_to
		} else {
			resetPassword.showDialog = false
			window.location.href = "/desk/peoplepay360"
		}
		if (response.verification?.setup) {
			otp.showDialog = true
			otp.tmp_id = response.tmp_id
			otp.verification = response.verification
		}
	} catch (error) {
		errorMessage.value = error.messages?.join("\n") || error.message || __("Login failed")
	}
}

const user_pass_login_disabled = createResource({
	url: "hrms.api.system_settings.get_user_pass_login_disabled",
	method: "GET",
	initialData: 0,
	auto: true,
})
</script>
