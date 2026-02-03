// Stub for Puter - disabled for local hosting
window.puter = {
    env: "web",
    auth: {
        isSignedIn: () => false,
        signIn: () => Promise.resolve(),
        signOut: () => {},
        getUser: () => Promise.resolve({})
    },
    ui: {
        showOpenFilePicker: () => Promise.resolve(null),
        showSaveFilePicker: () => Promise.resolve(null),
        onLaunchedWithItems: () => {}
    },
    ai: {
        chat: () => Promise.resolve("")
    }
};
