import React from "react";
import {
  FiMessageSquare,
  FiTwitter,
  FiFacebook,
  FiInstagram,
  FiGithub,
} from "react-icons/fi";

const Footer = () => {
  const iconStyles = {
    base: "flex items-center justify-center text-white transition-all duration-200 bg-transparent border border-white rounded-full w-7 h-7",
    hoverFocus:
      "focus:bg-orange-600 hover:text-white focus:text-white hover:bg-orange-600 hover:border-orange-600 focus:border-orange-600",
  };

  const linkClasses = {
    base: "flex text-sm text-white transition-all duration-200",
    hoverFocus: "hover:text-orange-600 focus:text-orange-600",
  };

  return (
    <section className="py-10 bg-black sm:pt-16 lg:pt-24">
      <div className="px-4 mx-auto sm:px-6 lg:px-8 max-w-7xl">
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-12 gap-y-12 gap-x-8 xl:gap-x-12">
          <div className="col-span-2 md:col-span-4 xl:pr-8">
            <h1 className="text-3xl font-medium text-white transition-all duration-200 hover:text-indigo-600">DbCli</h1>
            <p className="text-base leading-relaxed text-white mt-7">
              Build with precision. Get connected with DbCli and achieve seamless management and optimization of your databases.
            </p>
            <a
              href="#"
              title="Start Live Chat"
              className="inline-flex items-center justify-center px-6 py-4 font-semibold text-white transition-all duration-200 bg-blue-600 rounded-md hover:bg-blue-700 focus:bg-blue-700 mt-7"
            >
              <FiMessageSquare className="w-6 h-6 " />
              Start Live Chat
            </a>
          </div>

          {[
            {
              title: "Company",
              links: ["About", "Features", "Contact Us", "Careers"],
            },
            {
              title: "Help",
              links: [
                "Customer Support",
                "Getting Started",
                "Terms & Conditions",
                "Privacy Policy",
              ],
            },
            {
              title: "Resources",
              links: [
                "Database Migrations Guide",
                "CLI Command Documentation",
                "How to - Blog",
                "YouTube Tutorials",
              ],
            },
            {
              title: "Extra Links",
              links: [
                "Support Center",
                "API Documentation",
                "Community Forum",
                "Knowledge Base",
              ],
            },
          ].map((section, index) => (
            <div className="lg:col-span-2" key={index}>
              <p className="text-base font-semibold text-white">
                {section.title}
              </p>
              <ul className="mt-6 space-y-5">
                {section.links.map((link, idx) => (
                  <li key={idx}>
                    <a
                      href="#"
                      title={link}
                      className={`${linkClasses.base} ${linkClasses.hoverFocus}`}
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <hr className="mt-16 mb-10 border-gray-700" />

        <div className="sm:flex sm:items-center sm:justify-between">
          <p className="text-sm text-white">
            © Copyright 2024, All Rights Reserved by DbCli
          </p>

          <ul className="flex items-center mt-5 space-x-3 md:order-3 sm:mt-0">
            {[
              {
                icon: <FiTwitter className="w-4 h-4" />,
                href: "https://twitter.com",
              },
              {
                icon: <FiFacebook className="w-4 h-4" />,
                href: "https://facebook.com",
              },
              {
                icon: <FiInstagram className="w-4 h-4" />,
                href: "https://instagram.com",
              },
              {
                icon: <FiGithub className="w-4 h-4" />,
                href: "https://github.com",
              },
            ].map((item, index) => (
              <li key={index}>
                <a
                  href={item.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`${iconStyles.base} ${iconStyles.hoverFocus}`}
                >
                  {item.icon}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
};

export default Footer;
