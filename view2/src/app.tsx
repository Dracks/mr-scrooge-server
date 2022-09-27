import { AxiosError } from "axios";
import React from "react";

import { UserSession } from "./api/client/session/types";
import { useDeleteLogout } from "./api/client/session/use-delete-logout";
import { useGetSession } from "./api/client/session/use-get-session";
import { usePostLogin } from "./api/client/session/use-post-login";
import RestrictedContent from "./contents/restricted-content";
import { UserSessionContext } from "./contents/session/context";
import Login, { LoginCredentials } from "./contents/session/login";
import { LoadingPage } from "./utils/ui/loading";

import "./api/client/axios";

interface SessionStatus {
    data?: Partial<UserSession>;
    error?: AxiosError | null;
    loading: boolean;
}

const App: React.FC<{}> = () => {
    const [sessionRequest, reloadSession] = useGetSession();
    const [loginStatus, useLogin] = usePostLogin();
    const [, logout] = useDeleteLogout();

    const [sessionStatus, setSession] = React.useState<SessionStatus>({
        loading: sessionRequest.loading,
    });
    React.useEffect(() => {
        setSession({
            loading: sessionRequest.loading,
            data: sessionRequest.data,
            error: sessionRequest.error,
        });
    }, [sessionRequest]);

    const login = ({ username, password }: LoginCredentials) => {
        useLogin({ data: { user: username, password } }).then((response) => {
            setSession({
                ...sessionStatus,
                data: response.data,
            });
        });
    };

    if (sessionStatus.loading) {
        return <LoadingPage />;
    } else if (!sessionStatus.error) {
        if (sessionStatus.data && sessionStatus.data.isAuthenticated) {
            return (
                <UserSessionContext.Provider
                    value={{
                        ...(sessionStatus.data as UserSession),
                        logout: async () => {
                            await logout();
                            reloadSession();
                        },
                    }}
                >
                    <RestrictedContent />
                </UserSessionContext.Provider>
            );
        }
        return (
            <Login
                isLoading={loginStatus.loading}
                login={login}
                error={loginStatus.error}
                invalidCredentials={
                    loginStatus.data ? !loginStatus.data.isAuthenticated : false
                }
            />
        );
    }
    return <div>Error: {sessionStatus.error?.name}</div>;
};

export default App;
