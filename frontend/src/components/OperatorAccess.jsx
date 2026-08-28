import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import OperatorDashboard from "../pages/OperatorDashboard";
import OperatorLogin from "../pages/OperatorLogin";
import { supabase } from "../services/supabase";


export default function OperatorAccess() {
  const [operatorSession, setOperatorSession] =
    useState(null);
  const [loading, setLoading] = useState(true);
  const [accessError, setAccessError] = useState("");
  const validationId = useRef(0);

  const validateOperator = useCallback(async (session) => {
    const currentValidation = ++validationId.current;

    if (!session?.user) {
      setOperatorSession(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setAccessError("");

    const { data: profile, error } = await supabase
      .from("profiles")
      .select("role")
      .eq("id", session.user.id)
      .maybeSingle();

    if (currentValidation !== validationId.current) {
      return;
    }

    if (error || profile?.role !== "OPERATOR") {
      await supabase.auth.signOut();
      setOperatorSession(null);
      setAccessError(
        error
          ? "Unable to verify operator access"
          : "Operator access required"
      );
      setLoading(false);
      return;
    }

    setOperatorSession(session);
    setLoading(false);
  }, []);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      void validateOperator(data.session);
    });

    const { data: authListener } =
      supabase.auth.onAuthStateChange((_event, session) => {
        if (!session) {
          validationId.current += 1;
          setOperatorSession(null);
          setLoading(false);
        }
      });

    return () => {
      validationId.current += 1;
      authListener.subscription.unsubscribe();
    };
  }, [validateOperator]);

  const handleLogout = async () => {
    validationId.current += 1;
    await supabase.auth.signOut();
    setOperatorSession(null);
    setAccessError("");
  };

  if (loading) {
    return (
      <main className="page auth-page">
        <div className="loading-state" role="status">
          <span className="spinner" aria-hidden="true" />
          <p>Verifying operator access...</p>
        </div>
      </main>
    );
  }

  if (!operatorSession) {
    return (
      <OperatorLogin
        accessError={accessError}
        onAuthenticated={validateOperator}
      />
    );
  }

  return (
    <>
      <div className="operator-session-actions">
        <span><i aria-hidden="true" /> Operator · {operatorSession.user.email}</span>
        <button className="button button--ghost" type="button" onClick={handleLogout}>
          Logout
        </button>
      </div>

      <OperatorDashboard />
    </>
  );
}
