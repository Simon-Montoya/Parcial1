import { useState } from "react";

import { supabase } from "../services/supabase";


export default function OperatorLogin({
  accessError,
  onAuthenticated,
}) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const { data, error: signInError } =
        await supabase.auth.signInWithPassword({
          email,
          password,
        });

      if (signInError) {
        setError(
          /invalid login credentials/i.test(signInError.message)
            ? "Invalid credentials"
            : "Unable to sign in"
        );
        return;
      }

      await onAuthenticated(data.session);
    } catch {
      setError("Unable to sign in");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page auth-page">
      <section className="auth-card panel">
      <div className="auth-card__mark" aria-hidden="true">ER</div>
      <span className="eyebrow">Restricted workspace</span>
      <h1>Operator Access</h1>

      <p>
        Sign in with an authorized emergency operator
        account.
      </p>

      <form onSubmit={handleSubmit}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(event) =>
              setEmail(event.target.value)
            }
            autoComplete="email"
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
            autoComplete="current-password"
            required
          />
        </label>

        <button className="button button--primary" type="submit" disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>

      {(error || accessError) && (
        <p className="action-error" role="alert">
          {error || accessError}
        </p>
      )}
      </section>
    </main>
  );
}
