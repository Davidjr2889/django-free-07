import { defineStore } from "pinia";
import { $fetch } from "@/plugins/fetch";

function xorThis (key: string, str: string): string {
  let tmp;
  let xor = "";
  let j = 0;
  for (let i = 0; i < str.length; ++i) {
    tmp = str[i];
    if (j === key.length) {
      j = 0;
    }
    tmp = String.fromCharCode(tmp.charCodeAt(0) ^ key.charCodeAt(j));
    j++;
    xor += tmp;
  }
  return xor;
}

function cryptStr (key: string, astr: string): string {
  if (astr === undefined || astr === null) {
    return "";
  }
  return window.btoa(xorThis(key, astr));
}

function decryptStr (key: string, astr: string | null): string {
  if (astr === undefined || astr === null) {
    return "[]";
  }
  return xorThis(key, window.atob(astr));
}

export interface Token {
  token: string;
  expiresIn: number;
}

export interface RootState {
  jwtToken: Token | null;
  userId: number | null;
  userName: string | undefined;
  profileType: number | null;
  userPerms: string | null;
}

export const useMainStore = defineStore("main", {
  state: (): RootState => ({
    jwtToken: JSON.parse(
      sessionStorage.getItem("user-token") || "null",
    ) as Token,
    userId: JSON.parse(sessionStorage.getItem("userId") || "null") as
      | number
      | null,
    userName: sessionStorage.getItem("username") as string | undefined,
    profileType: JSON.parse(
      sessionStorage.getItem("profile-type") || "null",
    ) as number | null,
    userPerms: JSON.parse(
      decryptStr("anoc", sessionStorage.getItem("user-perms") || null),
    ) as string | null,
  }),
  getters: {
    token: (state) =>
      state.jwtToken !== undefined && state.jwtToken !== null
        ? state.jwtToken.token
        : null,
    token_expiration: (state) =>
      state.jwtToken !== undefined && state.jwtToken !== null
        ? state.jwtToken.expiresIn
        : null,
    username: (state) =>
      state.userName !== undefined && state.userName !== null
        ? state.userName
        : "",
    isAuthenticated: (state) => state.jwtToken != null,
    isAdminUser: (state) => state.profileType === 0,
    userHasPerm: (state) => (perm: string) => {
      if (state.userPerms) {
        return state.userPerms.indexOf(perm) >= 0;
      } else {
        return false;
      }
    },
  },
  actions: {
    async init () {
      // ...
    },
    async login (username: string, password: string) {
      try {
        this.jwtToken = await $fetch("lbb-api-token-auth/", {
          method: "POST",
          body: JSON.stringify({
            username: username,
            password: password,
          }),
        });
        this.userName = username;
        sessionStorage.setItem("user-token", JSON.stringify(this.jwtToken));
        sessionStorage.setItem("username", username);

        const profileData = await $fetch("get_user_profile/");
        this.userId = profileData.user_id;
        sessionStorage.setItem("userId", JSON.stringify(profileData.user_id));
        this.profileType = profileData.profile_type;
        sessionStorage.setItem(
          "profile-type",
          JSON.stringify(profileData.profile_type),
        );
        this.userPerms = profileData.os_perms;
        sessionStorage.setItem(
          "user-perms",
          cryptStr("anoc", JSON.stringify(profileData.os_perms)),
        );

        if (this.jwtToken !== null) {
          return true;
        }
        return false;
      } catch (e) {
        sessionStorage.removeItem("user-token");
        sessionStorage.removeItem("userId");
        sessionStorage.removeItem("username");
        sessionStorage.removeItem("profile-type");
        sessionStorage.removeItem("user-perms");
        throw e;
      }
    },

    logout () {
      sessionStorage.removeItem("user-token");
      this.jwtToken = null;
      sessionStorage.removeItem("userId");
      this.userId = null;
      sessionStorage.removeItem("username");
      this.userName = "";
      sessionStorage.removeItem("profile-type");
      this.profileType = null;
      sessionStorage.removeItem("user-perms");
      this.userPerms = null;
    },
  },
});
