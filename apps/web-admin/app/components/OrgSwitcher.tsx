"use client";

import { useEffect, useState } from "react";

import type { OrgResponse } from "@careos/types";

import { apiClient } from "../lib/api";

type Props = {
  fallbackOrgs: OrgResponse[];
};

export default function OrgSwitcher({ fallbackOrgs }: Props) {
  const [orgs, setOrgs] = useState<OrgResponse[]>(fallbackOrgs);

  useEffect(() => {
    let mounted = true;
    apiClient
      .getCurrentOrg()
      .then((org: OrgResponse) => {
        if (!mounted) {
          return;
        }
        setOrgs([org]);
      })
      .catch(() => {
        if (!mounted) {
          return;
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  const multiple = orgs.length > 1;

  return (
    <div className="row">
      <label htmlFor="org-switcher" className="status">
        Organization
      </label>
      <select id="org-switcher" className="input" disabled={!multiple}>
        {orgs.map((org: OrgResponse) => (
          <option key={org.id} value={String(org.id)}>
            {org.name}
          </option>
        ))}
      </select>
    </div>
  );
}
