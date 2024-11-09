import { FaApple, FaWindows, FaLinux } from "react-icons/fa";
import { MdCloudDownload } from "react-icons/md";

const CTA = () => {
  return (
    <section className="py-10 bg-black sm:py-16 lg:py-24">
      <div className="px-4 mx-auto sm:px-6 lg:px-8 max-w-7xl">
        <div className="max-w-2xl mx-auto text-center">
          <MdCloudDownload className="mx-auto w-14 h-14 text-white transition-transform transform hover:scale-110" />
          <h2 className="mt-10 text-3xl font-bold leading-tight text-white sm:text-4xl lg:text-5xl">
            Download DbCli
          </h2>
          <p className="max-w-xl mx-auto mt-4 text-base leading-relaxed text-gray-300">
            Unlock Your DbCli Experience
          </p>
        </div>

        <div className="flex flex-col items-center justify-center mt-8 space-y-4 md:space-y-0 md:space-x-4 md:flex-row lg:mt-12">
          {/* Download for Mac Button */}
          <a
            href="#"
            title="Download for Mac"
            className="inline-flex items-center justify-center px-4 py-4 text-white transition-all duration-300 transform border-2 border-white rounded-md hover:bg-white hover:text-black hover:scale-105 hover:shadow-lg focus:bg-white focus:text-black focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50"
            role="button"
          >
            <FaApple className="w-6 h-6 mr-2 -ml-1" />
            Download for Mac
          </a>

          {/* Download for Windows Button */}
          <a
            href="#"
            title="Download for Windows"
            className="inline-flex items-center justify-center px-4 py-4 text-white transition-all duration-300 transform border-2 border-white rounded-md hover:bg-white hover:text-black hover:scale-105 hover:shadow-lg focus:bg-white focus:text-black focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50"
            role="button"
          >
            <FaWindows className="w-6 h-6 mr-2 -ml-1" />
            Download for Windows
          </a>

          {/* Download for Linux Button */}
          <a
            href="#"
            title="Download for Linux"
            className="inline-flex items-center justify-center px-4 py-4 text-white transition-all duration-300 transform border-2 border-white rounded-md hover:bg-white hover:text-black hover:scale-105 hover:shadow-lg focus:bg-white focus:text-black focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50"
            role="button"
          >
            <FaLinux className="w-6 h-6 mr-2 -ml-1" />
            Download for Linux
          </a>
        </div>
      </div>
    </section>
  );
};

export default CTA;
